from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
import models
from bot_routers.general_buttons import back_markup, home_markup
from database import sessionLocal
from utils.actions import tap_to_coppy, escape
from raw_texts import BACK_TO_HOME


money, receipt = range(2)


async def getting_amount(update: Update, context: CallbackContext) -> None:
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
    return money


async def getting_receipt_photo(update: Update, context: CallbackContext) -> int:
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
    context.user_data["amount"] = amount
    context.user_data["user_id"] = update.effective_chat.id
    context.user_data["username"] = update.effective_user.username

    text = f" مبلغ {amount} تومان به شماره کارت زیر واریز کنید و عکس رسید آن را ارسال کنید "
    await update.effective_message.reply_text(
        f"{text}\n\n{tap_to_coppy('5859 8312 1872 8573')}",
        parse_mode="MarkdownV2",
    )

    return receipt


async def wait_for_confirm(update: Update, context: CallbackContext) -> int:
    if update.effective_message.text == BACK_TO_HOME:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="لغو شد.",
            reply_markup=home_markup,
        )
        return ConversationHandler.END
    elif update.effective_message.photo:

        photo = update.effective_message.photo[-1].file_id
        context.user_data["photo"] = photo

        user_id = context.user_data["user_id"]
        username = context.user_data["username"]
        amount = context.user_data["amount"]

        await update.effective_message.reply_text(
            "رسید شما ارسال شد. منتظر تایید باشید.",
            reply_markup=home_markup,
        )

        db = sessionLocal()

        admin = db.query(models.Admin).first()
        db.close()

        text = escape(f"@{username}\n\n{tap_to_coppy(user_id)}\n\n{amount}  تومان واریز کرده ")

        buttons_keys = [
            [
                InlineKeyboardButton(
                    "✅ تایید",
                    callback_data=f"Confirm_{user_id}_{amount}",
                ),
            ],
            [
                InlineKeyboardButton(
                    "❌ رد",
                    callback_data=f"Reject_{user_id}_{amount}"
                )
            ]
        ]
        buttons_markup = InlineKeyboardMarkup(buttons_keys)

        await context.bot.send_photo(
            chat_id=admin.Chat_Id,
            photo=photo,
            caption=text,
            reply_markup=buttons_markup,
            parse_mode="MarkdownV2",
        )

        return ConversationHandler.END


confirm, final_confirm = range(2)


async def confirm_receipt(update: Update, context: CallbackContext):
    action, user_id, amount = update.callback_query.data.split("_")

    text = update.effective_message.caption

    buttons_keys = [
        [
            InlineKeyboardButton(
                "✅ بله",
                callback_data=f"Final-Confirm_{user_id}_{amount}",
            ),
        ],
        [
            InlineKeyboardButton(
                "❌ خیر",
                callback_data=f"No-Confirm_{user_id}_{amount}"
            )
        ]
    ]
    buttons_markup = InlineKeyboardMarkup(buttons_keys)

    a = "تایید رسید کاربر؟"
    await update.effective_message.edit_caption(
        caption=escape(f"{text.replace(user_id, tap_to_coppy(user_id))}\n\n{a}"),
        reply_markup=buttons_markup,
        parse_mode="MarkdownV2",

    )


async def reject_receipt(update: Update, context: CallbackContext):
    action, user_id, amount = update.callback_query.data.split("_")

    text = update.effective_message.caption

    buttons_keys = [
        [
            InlineKeyboardButton(
                "✅ بله",
                callback_data=f"Final-Reject_{user_id}_{amount}",
            ),
        ],
        [
            InlineKeyboardButton(
                "❌ خیر",
                callback_data=f"No-Reject_{user_id}_{amount}"
            )
        ]
    ]
    buttons_markup = InlineKeyboardMarkup(buttons_keys)

    a = "رد رسید کاربر؟"
    await update.effective_message.edit_caption(
        caption=escape(f"{text.replace(user_id, tap_to_coppy(user_id))}\n\n{a}"),
        reply_markup=buttons_markup,
        parse_mode="MarkdownV2",

    )


async def final_confirm_receipt(update: Update, context: CallbackContext):
    action, user_id, amount = update.callback_query.data.split("_")

    text = update.effective_message.caption
    text = text.replace("تایید رسید کاربر؟", "").replace("رد رسید کاربر؟", "")

    a = " حساب کاربری شما"
    b = f"{amount} تومان شارژ شد "
    await context.bot.send_message(
        chat_id=user_id,
        text=f"{a}\n\n{b}",
    )
    a = "رسید کاربر تایید شد"
    await update.effective_message.edit_caption(
        caption=escape(f"{text.replace(user_id, tap_to_coppy(user_id))}{a}"),
        parse_mode="MarkdownV2",

    )


async def final_reject_receipt(update: Update, context: CallbackContext):
    action, user_id, amount = update.callback_query.data.split("_")

    text = update.effective_message.caption
    text = text.replace("تایید رسید کاربر؟", "").replace("رد رسید کاربر؟", "")

    await context.bot.send_message(
        chat_id=user_id,
        text=f"رسید شما رد شد",
    )
    a = "رسید کاربر رد شد"
    await update.effective_message.edit_caption(
        caption=escape(f"{text.replace(user_id, tap_to_coppy(user_id))}{a}"),
        parse_mode="MarkdownV2",
    )


async def wait_for_confirm_again(update: Update, context: CallbackContext):
    action, user_id, amount = update.callback_query.data.split("_")
    text = update.effective_message.caption
    text = text.replace("تایید رسید کاربر؟", "").replace("رد رسید کاربر؟", "")
    buttons_keys = [
        [
            InlineKeyboardButton(
                "✅ تایید",
                callback_data=f"Confirm_{user_id}_{amount}",
            ),
        ],
        [
            InlineKeyboardButton(
                "❌ رد",
                callback_data=f"Reject_{user_id}_{amount}"
            )
        ]
    ]
    buttons_markup = InlineKeyboardMarkup(buttons_keys)
    await update.effective_message.edit_caption(
        caption=escape(text.replace(user_id, tap_to_coppy(user_id))),
        reply_markup=buttons_markup,
        parse_mode="MarkdownV2",

    )
