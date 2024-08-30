from telegram import Update
from telegram.ext import CallbackContext
import models
from constants import  get_persian_number
from database import sessionLocal


async def get_rates_steps(data: dict, update: Update, context: CallbackContext):
    step = data["step"]

    # ----------------------------- Expire Message -------------------------

    # if await is_task_expired(update, context) and on_start != 0:
    #     await expired_message(update, context)
    #     return

    # ---------------------------- Wallet Management ------------------------

    if step == 0:
        db = sessionLocal()
        subscriptions = db.query(models.Subscriptions).order_by(
            # models.Subscriptions.Days,
            # models.Subscriptions.Number_Of_Users,
        ).all()

        days_filter = [i.Days for i in subscriptions]
        days_filter.sort()

        filtered = {i: [] for i in days_filter}

        for day in filtered.keys():
            for sub in subscriptions:
                if sub.Days == day:
                    filtered[day].append(sub)

        text = ""

        index = 0
        for items in filtered.items():
            day = items[0]
            subs = items[1]
            text += "\n\n"
            text += "💎 سرویس های "
            text += get_persian_number(int(day/30))
            text += " ماهه"
            for sub in subs:

                text += "\n"

                text += "🔸 " if index % 2 == 0 else "🔹 "
                text += get_persian_number(sub.Number_Of_Users)
                text += " کاربره: "
                if sub.Total_GB != 0:
                    text += str(sub.Total_GB)
                    text += " گیگ | "
                else:
                    text += " نامحدود | "
                text += str(sub.Price)
                text += " تومان"

                index += 1

        await context.bot.send_message(
            reply_to_message_id=update.effective_message.message_id,
            chat_id=update.effective_chat.id,
            text=text,
        )





