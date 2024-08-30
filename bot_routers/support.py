from telegram import Update
from telegram.ext import CallbackContext

import models
from database import sessionLocal
from raw_texts import CONNECTION_GUIDE_TEXT, SUPPORT, SUPPORT_TEXT
from utils.actions import server_not_available


async def support_steps(data: dict, update: Update, context: CallbackContext):
    step = data["step"]

    # ----------------------------- Expire Message -------------------------

    # if await is_task_expired(update, context) and on_start != 0:
    #     await expired_message(update, context)
    #     return

    # ---------------------------- Wallet Management ------------------------

    if step == 0:
        db = sessionLocal()

        meta_data = db.query(models.MetaData).first()

        if not meta_data:
            await server_not_available(update, context)
            return

        db.close()

        await context.bot.send_message(
            reply_to_message_id=update.effective_message.message_id,
            chat_id=update.effective_chat.id,
            text=SUPPORT_TEXT.replace('Support_Id', meta_data.Support_Id).replace('Channel_Id', meta_data.Channel_Id),
        )

