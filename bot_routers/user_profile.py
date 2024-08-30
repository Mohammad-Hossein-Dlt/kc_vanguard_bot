from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

import models
from database import sessionLocal
from utils.actions import add_task, is_task_expired, expired_message, server_not_available, callback_data_encoder, \
    tap_to_coppy, escape


async def user_profile_steps(data: dict, update: Update, context: CallbackContext):
    step = data["step"]

    # ----------------------------- Expire Message -------------------------

    # if await is_task_expired(update, context) and on_start != 0:
    #     await expired_message(update, context)
    #     return

    # ---------------------------- Wallet Management ------------------------

    if step == 0:
        db = sessionLocal()

        user = db.query(models.Users).where(
            models.Users.Chat_Id == update.effective_user.id
        ).first()

        users_services = db.query(models.UsersServices).where(
            models.UsersServices.User_Id == user.Id
        ).all()

        if not user or users_services.__contains__(None):
            await server_not_available(update, context)
            return

        db.close()

        buttons_keys = [
            # [
            #     InlineKeyboardButton(
            #         "سوابق پرداخت",
            #         callback_data="None"
            #     ),
            # ],
            [
                InlineKeyboardButton(
                    "❌  بستن پنل",
                    callback_data="close"
                )
            ]
        ]
        buttons_markup = InlineKeyboardMarkup(buttons_keys)

        user_id = "آیدی شما:"
        user_services = "تعداد سرویس های شما:"

        await context.bot.send_message(
            reply_to_message_id=update.effective_message.message_id,
            chat_id=update.effective_chat.id,
            text=escape(f'{user_id}  {tap_to_coppy(update.effective_user.id)}\n\n{user_services}  {len(users_services)}'),
            reply_markup=buttons_markup,
            parse_mode="MarkdownV2",
        )
