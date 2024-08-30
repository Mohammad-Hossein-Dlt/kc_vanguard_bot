from fastapi import APIRouter, status
import constants
import models
from db_dependency import db_dependency

router = APIRouter(prefix="/user", tags=["user"])


@router.post('/edit_wallet', status_code=status.HTTP_200_OK)
async def edit_wallet(
        db: db_dependency,
        user_id: str,
        amount: int,
        plus_or_minus: constants.UserWalletPlusOrMinus,
):
    user = db.query(models.Users).where(
        models.Users.Chat_Id == user_id
    ).first()

    if user:

        if plus_or_minus == constants.UserWalletPlusOrMinus.plus:
            user.Wallet += amount

        if plus_or_minus == constants.UserWalletPlusOrMinus.minus:
            user.Wallet -= amount

        db.commit()

        return "User's wallet edited"

    return "No user exist"
