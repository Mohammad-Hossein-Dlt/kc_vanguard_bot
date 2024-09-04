import models
from bot_routers.connection_guide import connection_guide_steps
from bot_routers.general_buttons import home_markup
from bot_routers.buy import buy_steps
from bot_routers.get_rates import get_rates_steps
from bot_routers.support import support_steps
from bot_routers.user_profile import user_profile_steps
from bot_routers.wallet import wallet_steps
from bot_routers.free_test import free_test
from bot_routers.services_manage import services_manage_steps
from config import API_TOKEN
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackContext,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler,
    JobQueue,
)
from database import sessionLocal
from utils.actions import (
    delete_expired_task,
    callback_data_decoder,
    check_server_enabled,
)
from bot_routers.send_receipt import (
    getting_amount,
    getting_receipt_photo,
    wait_for_confirm,
    confirm_receipt,
    reject_receipt,
    final_confirm_receipt,
    final_reject_receipt,
    wait_for_confirm_again,
    money,
    receipt
)
from bot_routers.riali_payment import rial_amount, rial_get_amount, rial_payment
from bot_routers.send_voucher import voucher_code, get_code, verify_code
from raw_texts import *


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = sessionLocal()

    check = db.query(models.Users).where(
        models.Users.Chat_Id == update.effective_chat.id
    ).first()

    if not check:
        user = models.Users()

        user.Chat_Id = update.effective_chat.id
        # user.Wallet = 100000

        db.add(user)

        db.commit()

    db.close()

    hello = "سلام 👋"

    wellcome = "به ربات فروشگاه کیسی ونگارد خوش اومدین 🌹"

    message = "لطفا یکی از گزینه های زیر را انتخاب کنید."

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"{hello}\n\n{wellcome}\n\n{message}",
        reply_markup=home_markup,
    )


async def home_button_handler(update: Update, context: CallbackContext) -> None:
    text = update.effective_message.text

    if not await check_server_enabled(update, context):
        return

    if text == BUY_SERVICE:
        await buy_steps({"sec": "buy", "step": 0, "i_id": 0, "u": "", "m": "", "gb": ""}, update, context)

    if text == FREE_TEST:
        await free_test({"sec": "free_test", "step": 0, "i_id": 0}, update, context)

    if text == WALLET:
        await wallet_steps({"sec": "wa", "step": 0, "on-start": 0}, update, context)

    if text == RATES:
        await get_rates_steps({"step": 0}, update, context)

    if text == SERVICE_MANAGEMENT:
        await services_manage_steps({"id": 0, "sec": "sm", "step": 0}, update, context)

    if text == CONNECTION_GUIDE:
        await connection_guide_steps({"step": 0}, update, context)

    if text == USER_PROFILE:
        await user_profile_steps({"step": 0}, update, context)

    if text == SUPPORT:
        await support_steps({"step": 0}, update, context)

    if text == BACK_TO_HOME:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.message.message_id,
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='یکی از گزینه های زیر را انتخاب کنید',
            reply_markup=home_markup,
            # parse_mode='MarkdownV2'
        )


async def callback_button_handler(update: Update, context: CallbackContext) -> None:
    command = update.callback_query.data

    if not await check_server_enabled(update, context):
        return

    if "close" in command:
        # await update.callback_query.delete_message()
        await delete_expired_task(update, context)
        try:
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

    else:
        decode, permission = callback_data_decoder(command)
        if permission:
            if decode["sec"] == "buy":
                await buy_steps(decode, update, context)

            if decode["sec"] == "wa":
                await wallet_steps(decode, update, context)

            if decode["sec"] == "free_test":
                await free_test(decode, update, context)

            if decode["sec"] == "sm":
                await services_manage_steps(decode, update, context)


async def forward_message(update: Update, context: CallbackContext):
    print("++++++++++++++++++++++++++++++")

    db = sessionLocal()

    admin = db.query(models.Admin).where(
        models.Admin.Chat_Id == update.effective_user.id
    ).first()

    if admin:

        # settings = db.query(models.Setting).first()
        # bot_member = await context.bot.get_chat_member(
        #     chat_id=update.effective_message.chat_id,
        #     user_id=context.bot.id,
        # )

        # if bot_member.status == ChatMember.ADMINISTRATOR:

        users = db.query(models.Users).all()
        for user in users:
            try:
                if user.Chat_Id == admin.Chat_Id:
                    await context.bot.send_message(
                        chat_id=admin.Chat_Id,
                        text=str(update.effective_message.message_id)
                    )
                else:
                    await context.bot.forward_message(
                        chat_id=user.Chat_Id,
                        from_chat_id=update.effective_message.chat_id,
                        message_id=update.effective_message.message_id,
                    )
            except Exception as ex:
                print(ex)
                print(f"Failed to send message to {user.Chat_Id}.")
    db.close()


async def cancel_conversation(update: Update, context: CallbackContext) -> int:
    await update.effective_message.reply_text(
        "لغو شد.",
        reply_markup=home_markup,
    )

    return ConversationHandler.END


def main():
    job = JobQueue()
    bot = ApplicationBuilder().token(API_TOKEN).job_queue(job).build()

    send_receipt_conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(getting_amount, pattern="start_send_receipt")],
        states={
            money: [
                MessageHandler(filters.TEXT, getting_receipt_photo)
            ],
            receipt: [
                MessageHandler(filters.PHOTO | filters.TEXT, wait_for_confirm)
            ],
        },
        fallbacks=[]
    )

    send_voucher_conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(get_code, pattern="send_voucher")],
        states={
            voucher_code: [
                MessageHandler(filters.TEXT, verify_code)
            ],
        },
        fallbacks=[]
    )

    rial_payment_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(rial_get_amount, pattern="rial_payment")],
        states={
            rial_amount: [
                MessageHandler(filters.TEXT, rial_payment)
            ],
        },
        fallbacks=[]
    )

    bot.add_handlers(
        [
            CallbackQueryHandler(confirm_receipt, pattern="Confirm_*"),
            CallbackQueryHandler(final_confirm_receipt, pattern="Final-Confirm_*"),
            CallbackQueryHandler(wait_for_confirm_again, pattern="No-Confirm_*"),

            CallbackQueryHandler(reject_receipt, pattern="Reject_*"),
            CallbackQueryHandler(final_reject_receipt, pattern="Final-Reject_*"),
            CallbackQueryHandler(wait_for_confirm_again, pattern="No-Reject_*"),
        ]
    )

    bot.add_handlers([
        send_receipt_conversation_handler,
        rial_payment_handler,
        send_voucher_conversation_handler,
        CommandHandler("start", start),
        MessageHandler(filters.FORWARDED, forward_message),
        MessageHandler(filters.TEXT & ~filters.COMMAND, home_button_handler),
        CallbackQueryHandler(callback_button_handler),
    ])

    bot.run_polling()


if __name__ == '__main__':
    main()

# asyncio.run(create_db())
# models.Base.metadata.create_all(bind=engine)
