from fastapi import APIRouter, Request, status
from fastapi.templating import Jinja2Templates
import models
from db_dependency import db_dependency
from utils.parse_null import parse_null
from utils.response_model import ResponseMessage

router = APIRouter(prefix="/setting", tags=["setting"])
templates = Jinja2Templates(directory='templates')


@router.get('/fetch', status_code=status.HTTP_200_OK)
async def get(
        db: db_dependency,
):
    settings = db.query(models.Setting).first()

    if settings:
        return settings

    return dict()


@router.put('/edit', status_code=status.HTTP_201_CREATED)
async def create(
        db: db_dependency,
        enable: bool | None = None,
):

    enable = parse_null(enable)

    settings = db.query(models.Setting).first()

    if settings:

        settings.Enabled = enable if enable is not None else settings.Enabled

    else:
        settings = models.Setting()
        settings.Enabled = enable

        db.add(settings)

    db.commit()

    return ResponseMessage(error=False, message={
            "text": "settings edited.",
        },
    )


@router.delete('/delete', status_code=status.HTTP_200_OK)
async def delete(
        db: db_dependency,
        settings_id: int,
):
    settings = db.query(models.Setting).where(
        models.Setting.Id == settings_id,
    ).first()

    if settings:
        db.delete(settings)
        db.commit()

    return ResponseMessage(error=False, message={
            "text": "settings deleted.",
        },
    )
