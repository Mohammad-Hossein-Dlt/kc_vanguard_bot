from fastapi import APIRouter, status
import models
from db_dependency import db_dependency
from utils.parse_null import parse_null
from utils.response_model import ResponseMessage

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get('/fetch_all', status_code=status.HTTP_200_OK)
async def get(
        db: db_dependency,
):
    admins = db.query(models.Admin).all()

    if admins:
        return admins

    return dict()


@router.get('/fetch_one', status_code=status.HTTP_200_OK)
async def edit_wallet(
        db: db_dependency,
        user_id: int,
):
    admin = db.query(models.Admin).where(
        models.Admin.Id == user_id
    ).first()

    if admin:
        return admin

    return dict()


@router.post('/insert', status_code=status.HTTP_200_OK)
async def edit_wallet(
        db: db_dependency,
        chat_id: int,
        super_admin: bool,
):
    admin = db.query(models.Admin).where(
        models.Admin.Chat_Id == chat_id
    ).first()

    if not admin:
        new_admin = models.Admin()

        new_admin.Chat_Id = chat_id
        new_admin.SuperAdmin = super_admin

        db.add(new_admin)
        db.commit()

        return ResponseMessage(error=False, message="new admin inserted.")

    return ResponseMessage(error=False, message="the admin is exist.")


@router.put('/edit', status_code=status.HTTP_200_OK)
async def edit_wallet(
        db: db_dependency,
        admin_id: int,
        chat_id: int | None = None,
        super_admin: bool | None = None,
):
    chat_id = parse_null(chat_id)
    super_admin = parse_null(super_admin)

    admin = db.query(models.Admin).where(
        models.Admin.Id == admin_id
    ).first()

    if admin:
        super_admins = db.query(models.Admin).where(
            models.Admin.SuperAdmin == True
        ).all()

        admin.Chat_Id = chat_id if chat_id is not None else admin.Chat_Id
        admin.SuperAdmin = super_admin if super_admin is not None else admin.SuperAdmin

        edit_super_admin = True

        if super_admin == False and (super_admins is not None or super_admins.__contains__(None) == False):
            for index, sa in enumerate(super_admins):
                if sa.Id == admin.Id:
                    super_admins.pop(index)

            if len(super_admins) < 1:
                edit_super_admin = False

        if not edit_super_admin:
            return ResponseMessage(error=True, message="there should be at least one super admin.")

        db.commit()
        return ResponseMessage(error=False, message="admin edited.")

    return ResponseMessage(error=False, message="no admin exist.")


@router.delete('/delete', status_code=status.HTTP_200_OK)
async def edit_wallet(
        db: db_dependency,
        user_id: int,
):
    admin = db.query(models.Admin).where(
        models.Admin.Id == user_id
    ).first()

    if admin:
        db.delete(admin)
        db.commit()

    return ResponseMessage(error=False, message="admin deleted.")
