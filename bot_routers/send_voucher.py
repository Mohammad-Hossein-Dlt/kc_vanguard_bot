from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from bot_routers.general_buttons import back_markup, home_markup
from raw_texts import BACK_TO_HOME
voucher_code = 0


async def get_code(update: Update, context: CallbackContext) -> int:
    query = update.callback_query

    await query.answer()

    text = '''

پرداخت با ووچر پرفکت مانی بصورت مستقیم و   آنی 💳


ووچر پرفکت مانی شبیه گیفت کارت یک کد در اختیار شما قرار میده و با استفاده از کدی که خریداری کردید میتونید کانفیگ مد نظر رو خرید کنید ✅ 

وارد سایت cafearz.com بشید و به قیمت کانفیگی که میخاید ووچر پرفکت مانی خریداری کنید 📥 

بعد از خرید ، ( کد فعال سازی ) و ( کد ووچر ) در اختیار شما قرار میگیره

کد فعال سازی و کد ووچر رو به همراه / بعد از این پیام بفرستید

voucher_code/activate_code
کد فعال سازی/کد ووچر

از تمامی سایت ها میتونید ووچر پرفکت مانی تهیه کنید 📍
    
    '''
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id,
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=back_markup,
    )
    return voucher_code


async def verify_code(update: Update, context: CallbackContext) -> int:

    if update.effective_message.text == BACK_TO_HOME:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="لغو شد.",
            reply_markup=home_markup,
        )
        return ConversationHandler.END

    text = "کد معتبر است."

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=home_markup,
    )
    return ConversationHandler.END
