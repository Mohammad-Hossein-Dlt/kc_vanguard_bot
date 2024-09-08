from fastapi import APIRouter, status
import models
from config import API_TOKEN
from db_dependency import db_dependency
from utils.parse_null import parse_null
from utils.response_model import ResponseMessage
from telegram import Bot

router = APIRouter(prefix="/message", tags=["Send_Message"])

bot = Bot(token=API_TOKEN)


@router.post('/send', status_code=status.HTTP_200_OK)
async def send(
        db: db_dependency,
        message: str,
):
    users = db.query(models.Users).all()
    try:
        for user in users:
            await bot.send_message(
                chat_id=user.Chat_Id,
                text=message,
            )

        return ResponseMessage(error=False, message={
            "text": "message sent.",
        },
        )

    except Exception as ex:
        print(ex)
        return ResponseMessage(error=False, message={
            "text": "failed to send message",
        },
        )


@router.delete('/delete', status_code=status.HTTP_200_OK)
async def delete(
        db: db_dependency,
        message_id: int,
):
    users = db.query(models.Users).all()

    for user in users:
        try:

            await bot.delete_message(
                chat_id=user.Chat_Id,
                message_id=message_id,
            )

        except Exception as ex:
            print(ex)
            print(f"Failed to deleted message from {user.Chat_Id}.")

    return ResponseMessage(error=False, message="message deleted.")
