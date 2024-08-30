import models
from database import sessionLocal


async def check_admin(chat_id: int):
    db = sessionLocal()
    admin = db.query(models.Admin).where(
        models.Admin.Chat_Id == chat_id
    ).first()

    db.close()

    return True if admin else False

