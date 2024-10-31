from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

import models
from database import sessionLocal
from raw_texts import BACK
from utils.actions import add_task, is_task_expired, expired_message, server_not_available, callback_data_encoder


async def wallet_steps(data: dict, update: Update, context: CallbackContext):
    step = data["step"]
    on_start = data["on-start"]

    # ----------------------------- Expire Message -------------------------

    if await is_task_expired(update, context) and on_start != 0:
        await expired_message(update, context)
        return

    # ---------------------------- Wallet Management ------------------------

    if step == 0:
        db = sessionLocal()
        user = db.query(models.Users).where(
            models.Users.Chat_Id == update.effective_chat.id
        ).first()

        if not user:
            await server_not_available(update, context)
            return

        data["step"] = 1

        buttons_keys = [
            [
                InlineKeyboardButton(
                    "شارژ کیف پول",
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

        db.close()

        wallet_credit = f" اعتبار کیف پول شما:\n\n{user.Wallet} تومان"

        if on_start == 0:
            message = await context.bot.send_message(
                reply_to_message_id=update.effective_message.message_id,
                chat_id=update.effective_chat.id,
                text=wallet_credit,
                reply_markup=buttons_markup,
            )
            await add_task(update.effective_user.id, message.message_id)

        if on_start == -1:
            await update.effective_message.edit_text(
                text=wallet_credit,
                reply_markup=buttons_markup,
            )

    if step == 1:
        back_state = data.copy()
        back_state["on-start"] = -1
        back_state["step"] = 0

        buttons_key = [
            # [
            #     InlineKeyboardButton(
            #         "ارسال رسید",
            #         callback_data="start_send_receipt",
            #     )
            # ],
            [
                InlineKeyboardButton(
                    "پرداخت ریالی",
                    callback_data="rial_payment",
                )
            ],
            # [
            #     InlineKeyboardButton(
            #         "اعمال ووچر پرفکت مانی",
            #         callback_data="send_voucher"
            #     )
            # ],
            [
                InlineKeyboardButton(
                    BACK,
                    callback_data=callback_data_encoder(back_state),
                ),
            ],
            [
                InlineKeyboardButton(
                    "❌  بستن پنل",
                    callback_data="close"
                )
            ]
        ]

        buttons_markup = InlineKeyboardMarkup(buttons_key)

        choose_payment_method = "روش پرداخت را انتخاب کنید"
        await update.effective_message.edit_text(
            text=choose_payment_method,
            reply_markup=buttons_markup,
        )
