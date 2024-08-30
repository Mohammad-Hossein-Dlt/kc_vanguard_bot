from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from raw_texts import CONNECTION_GUIDE_TEXT


async def connection_guide_steps(data: dict, update: Update, context: CallbackContext):
    step = data["step"]

    # ----------------------------- Expire Message -------------------------

    # if await is_task_expired(update, context) and on_start != 0:
    #     await expired_message(update, context)
    #     return

    # ---------------------------- Wallet Management ------------------------

    if step == 0:
        buttons_keys = [
            [
                InlineKeyboardButton(
                    "android",
                    url="google.com",
                )
            ],
            [
                InlineKeyboardButton(
                    "ios",
                    url="google.com",
                )
            ],
            [
                InlineKeyboardButton(
                    "windows",
                    url="google.com",
                )
            ],
            [
                InlineKeyboardButton(
                    "❌  بستن پنل",
                    callback_data="close"
                )
            ]
        ]
        buttons_markup = InlineKeyboardMarkup(buttons_keys)

        await context.bot.send_message(
            reply_to_message_id=update.effective_message.message_id,
            chat_id=update.effective_chat.id,
            text=CONNECTION_GUIDE_TEXT,
            reply_markup=buttons_markup,
        )
