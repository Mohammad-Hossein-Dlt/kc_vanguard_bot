from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
import models
from bot_routers.buy import buy_steps
from bot_routers.general_buttons import back_markup, home_markup
from bot_routers.services_manage import services_manage_steps
from database import sessionLocal
from raw_texts import BACK_TO_HOME

code_state = 0


async def send_discount_code(update: Update, context: CallbackContext) -> int:
    query = update.callback_query

    await query.answer()

    text = "🎁 لطفا کد تخفیف هدیه خود را ارسال کنید"
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id,
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=back_markup,
    )
    return code_state


async def apply_discount_code(update: Update, context: CallbackContext) -> int:

    if update.effective_message.text == BACK_TO_HOME:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="لغو شد.",
            reply_markup=home_markup,
        )
        return ConversationHandler.END

    data = context.user_data["data"]

    code = update.effective_message.text

    db = sessionLocal()

    discount = db.query(models.DiscountCodes).where(
        models.DiscountCodes.Code == code
    ).first()

    single_subscription = db.query(models.Subscriptions).where(
        models.Subscriptions.Id == data["gb"]
    ).first()

    subscription = db.query(models.Subscriptions).distinct().where(
        models.Subscriptions.Number_Of_Users == single_subscription.Number_Of_Users,
        models.Subscriptions.Days == single_subscription.Days,
        models.Subscriptions.Total_GB == single_subscription.Total_GB,
    ).first()

    db.close()

    if not discount:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ کد تخفیف یافت نشد",
        )
        return ConversationHandler.END

    deducted = (subscription.Price * discount.Percent) / 100
    a = "🥳 کد تخفیف با موفقیت ثبت شد و مبلغ "
    b = " تومان از قیمت سرویس مورد نظر کسر شد"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"{a}{int(deducted)}{b}",
    )

    data = context.user_data["data"]
    data["d_c"] = discount.Percent
    if data["sec"] == "buy":
        await buy_steps(data, update, context)

    if data["sec"] == "sm":
        await services_manage_steps(data, update, context)
    return ConversationHandler.END



