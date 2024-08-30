from datetime import datetime, timedelta

import pytz
from telegram import Update
from telegram.ext import CallbackContext
import models
from database import sessionLocal
from sqlalchemy import and_


async def add_task(
        user_id: int,
        user_message_id: int,
):
    db = sessionLocal()

    user = db.query(models.Users).where(
        models.Users.Chat_Id == user_id,
    ).first()

    new_task = models.UsersTasks()

    new_task.User_Id = user.Id
    new_task.Message_Id = user_message_id
    new_task.ExpirationDate = datetime.now(pytz.UTC) + timedelta(minutes=5)

    db.add(new_task)

    db.commit()
    db.close()


async def delete_expired_task(
        update: Update,
        context: CallbackContext,
):
    db = sessionLocal()

    user = db.query(models.Users).where(
        models.Users.Chat_Id == update.effective_user.id,
    ).first()

    task = db.query(models.UsersTasks).where(
        and_(
            models.UsersTasks.User_Id == user.Id,
            models.UsersTasks.Message_Id == update.effective_message.message_id,
        )
    ).first()

    if task:
        db.delete(task)

    db.commit()
    db.close()


async def expired_message(
        update: Update,
        context: CallbackContext,
):
    await delete_expired_task(update, context)

    try:
        await update.callback_query.answer(
            text="این پیام منقضی شده است!",
            show_alert=True,
        )
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id,
        )
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.reply_to_message.message_id,
        )
    except Exception as ex:
        pass


async def is_task_expired(update: Update, context: CallbackContext):
    db = sessionLocal()
    time_now = datetime.now(pytz.UTC)

    user = db.query(models.Users).where(
        models.Users.Chat_Id == update.effective_user.id,
    ).first()

    expired_task = db.query(models.UsersTasks).where(
        and_(
            models.UsersTasks.User_Id == user.Id,
            models.UsersTasks.Message_Id == update.effective_message.message_id,
            models.UsersTasks.ExpirationDate < time_now,
        )
    ).first()

    no_expired_task = db.query(models.UsersTasks).where(
        and_(
            models.UsersTasks.User_Id == user.Id,
            models.UsersTasks.Message_Id == update.effective_message.message_id,
            models.UsersTasks.ExpirationDate > time_now,
        )
    ).first()

    db.close()

    if expired_task:
        return True

    if no_expired_task:
        return False

    if not expired_task and not no_expired_task:
        return True

    return False


async def server_not_available(update: Update, context: CallbackContext):
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="سرور در دسترس نیست!",
        # show_alert=True,
    )


async def check_server_enabled(update: Update, context: CallbackContext):
    db = sessionLocal()

    settings = db.query(models.Setting).first()

    admin = db.query(models.Admin).first()

    if admin.Chat_Id == update.effective_user.id:
        return True

    if settings.Enabled:
        return True

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="سرور غیرفعال است!",
        # show_alert=True,
    )

    db.close()

    return False


def escape(text: str):
    chars = [
        "_",
        "*",
        "[",
        "]",
        "{",
        "}",
        "(",
        ")",
        "~",
        ">",
        "#",
        "+",
        "-",
        "+",
        "=",
        "|",
        ".",
        "!"
        "`",
    ]
    for i in chars:
        text = text.replace(i, f"\\{i}")

    return text


def tap_to_coppy(test):
    # return "`" + test + "`"
    return f"`{test}`"


def callback_data_decoder(data: str) -> dict and int:
    def check(item: str) -> bool:
        if item == '':
            return False
        if ':' not in item:
            return False
        if len(item[:item.index(':')]) == 0 or len(item[item.index(':'):]) == 0:
            return False

        return True

    try:
        data = data.split(',')
        data = list(filter(lambda x: check(x), data))
        dict_data = dict()
        for i in data:
            key, value = i.split(':')
            # if value.isnumeric():
            #     value = int(value)

            try:
                value = int(value)
            except ValueError as ex:
                pass

            dict_data[key] = value

        if len(dict_data) == 0:
            return dict_data, False
        return dict_data, True
    except Exception as ex:
        print(ex)
        return data, False


def callback_data_encoder(dict_data: dict) -> dict and int:
    str_data = ''

    for key, value in dict_data.items():
        str_data += f'{key}:{value},'

    return str_data
