from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from constants import gb_size
from panel_api import add_client
import models
from database import sessionLocal
from raw_texts import BACK
from utils.actions import (
    add_task,
    is_task_expired,
    expired_message,
    tap_to_coppy,
    callback_data_encoder,
    server_not_available, escape,
)
from utils.expire_time import expiration_time


async def free_test(data: dict, update: Update, context: CallbackContext):
    step = data["step"]
    inbound_id = data["i_id"]

    # ----------------------------- Expire Message -------------------------

    if await is_task_expired(update, context) and inbound_id != 0:
        await expired_message(update, context)
        return

    # ----------------------------- Get Free Test --------------------------

    if step == 0:
        db = sessionLocal()

        user = db.query(models.Users).where(
            models.Users.Chat_Id == update.effective_user.id
        ).first()

        admin = db.query(models.Admin).where(
            models.Admin.Chat_Id == update.effective_user.id
        ).first()

        if not user:
            await server_not_available(update, context)
            return

        if user.TestAccount and not admin:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️  شما قبلا تست رایگان دریافت کردید",
            )
        else:
            data["step"] = 1

            buttons_keys = [
                [
                    InlineKeyboardButton(
                        "دریافت تست رایگان",
                        callback_data=callback_data_encoder(data)
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "❌  بستن پنل",
                        callback_data="close"
                    )
                ]
            ]
            buttons_markup = InlineKeyboardMarkup(buttons_keys)

            get_free_test = "✅  برای دریافت تست رایگان گزینه زیر را انتخاب کنید"
            if inbound_id == 0:
                message = await context.bot.send_message(
                    reply_to_message_id=update.effective_message.message_id,
                    chat_id=update.effective_chat.id,
                    text=get_free_test,
                    reply_markup=buttons_markup,
                )
                await add_task(update.effective_user.id, message.message_id)
            if inbound_id == -1:
                await update.effective_message.edit_text(
                    text=get_free_test,
                    reply_markup=buttons_markup,
                )
        db.close()

    if step == 1:
        db = sessionLocal()
        inbounds = db.query(models.TestInbounds).all()

        if not inbounds:
            await server_not_available(update, context)
            return

        buttons_keys = []

        for i in inbounds:
            callback_data = data.copy()
            callback_data["i_id"] = i.Id
            callback_data["step"] = 2
            encode = callback_data_encoder(callback_data)

            buttons_keys.append(
                [
                    InlineKeyboardButton(
                        i.Remark,
                        callback_data=encode,
                    ),
                ]
            )

        back_state = data.copy()
        back_state["i_id"] = -1
        back_state["step"] = 0

        buttons_keys.append(
            [
                InlineKeyboardButton(
                    BACK,
                    callback_data=callback_data_encoder(back_state),
                ),
            ]
        )

        buttons_keys.append(
            [
                InlineKeyboardButton(
                    "❌  بستن پنل",
                    callback_data="close"
                )
            ]
        )

        buttons_markup = InlineKeyboardMarkup(buttons_keys)

        db.close()

        get_free_test = "🔥 دریافت تست رایگان"
        choose_location = "کشور مورد نظر را انتخاب کنید"
        await update.effective_message.edit_text(
            text=f'{get_free_test}\n\n{choose_location}',
            reply_markup=buttons_markup,
        )

    if step == 2:
        db = sessionLocal()

        inbound_id = data["i_id"]

        server, inbound = db.query(models.Servers, models.TestInbounds).join(
            models.TestInbounds
        ).where(
            models.TestInbounds.Id == inbound_id
        ).first()

        user = db.query(models.Users).where(
            models.Users.Chat_Id == update.effective_chat.id,
        ).first()

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="درحال ساخت کانفیگ...",
        )

        expire_time, raw_time = expiration_time(days=1)

        config_url = add_client(
            panel_url=server.Url,
            username=server.UserName,
            password=server.Password,
            address=inbound.Address,
            sni=inbound.Sni,
            inbound_id=inbound.Panel_Inbound_Id,
            ip_limit=1,
            expire_time=expire_time,
            total_gb=1 * gb_size,
        )

        if not server or not inbound or not user or not config_url:
            await server_not_available(update, context)
            return

        user.TestAccount = True

        user_service = models.UsersServices()

        user_service.Test_Inbound_Id = inbound.Id
        user_service.Subscription_Id = None
        user_service.User_Id = user.Id
        user_service.Email = config_url[1]
        user_service.UUID = config_url[2]
        user_service.Days = 1
        user_service.Number_Of_Users = 1
        user_service.ExpirationDate = raw_time
        user_service.Total_GB = 1 * gb_size

        db.add(user_service)

        db.commit()

        db.close()

        a = "تست رایگان شما"
        b = "حجم: 1 گیگ"
        c = "زمان: 1 روزه"

        await update.effective_message.delete()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=escape(f"{a}\n\n{b}\n\n{c}\n\n{tap_to_coppy(config_url[0])}"),
            parse_mode="MarkdownV2"
        )
