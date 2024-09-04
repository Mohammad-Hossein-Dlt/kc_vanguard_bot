from fastapi import APIRouter, status
import models
from db_dependency import db_dependency
from utils.response_model import ResponseMessage

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get('/fetch', status_code=status.HTTP_200_OK)
async def get(
        db: db_dependency,
):
    admins = db.query(models.Admin).all()

    if admins:
        return admins

    return dict()


@router.post('/insert', status_code=status.HTTP_200_OK)
async def edit_wallet(
        db: db_dependency,
        user_id: int,
):
    admin = db.query(models.Admin).where(
        models.Admin.Chat_Id == user_id
    ).first()

    if not admin:
        new_admin = models.Admin()

        new_admin.Chat_Id = user_id

        db.add(new_admin)
        db.commit()

        return ResponseMessage(error=False, message="new admin inserted.")

    return ResponseMessage(error=False, message="the admin is exist.")


@router.delete('/delete', status_code=status.HTTP_200_OK)
async def edit_wallet(
        db: db_dependency,
        user_id: int,
):
    admin = db.query(models.Admin).where(
        models.Admin.Chat_Id == user_id
    ).first()

    if admin:
        db.delete(admin)
        db.commit()

    return ResponseMessage(error=False, message="admin deleted.")
