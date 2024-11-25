from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from bot_routers.general_buttons import back_markup, home_markup
import uuid

from config import SERVER_URL
from raw_texts import BACK_TO_HOME
rial_amount = 0


async def rial_get_amount(update: Update, context: CallbackContext) -> int:
    query = update.callback_query

    await query.answer()

    text = "مبلغی که میخواهید کیف پولتان را شارژ کنید وارد کنید"
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id,
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=back_markup,
    )
    return rial_amount


async def rial_payment(update: Update, context: CallbackContext) -> int:
    if update.effective_message.text == BACK_TO_HOME:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="لغو شد.",
            reply_markup=home_markup,
        )
        return ConversationHandler.END

    amount = update.effective_message.text

    if not amount.isnumeric():
        await update.effective_message.reply_text(
            "لطفا عدد انگلیسی وارد کنید.",
            reply_markup=home_markup,
        )
        return ConversationHandler.END

    payment_url = f"{SERVER_URL}/api/v2/payment/request/?user_id={update.effective_user.id}&payment_id={uuid.uuid4()}&amount={amount}"

    text = f" مبلغ {amount} تومان را از طریق لینک زیر پرداخت کنید "

    buttons_keys = [
        [
            InlineKeyboardButton(
                "✅ پرداخت",
                url=payment_url,
            ),
        ],

    ]

    buttons_markup = InlineKeyboardMarkup(buttons_keys)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=buttons_markup,
    )
    return ConversationHandler.END
