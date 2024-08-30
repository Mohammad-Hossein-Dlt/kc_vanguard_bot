from fastapi import APIRouter, Request, status
from fastapi.templating import Jinja2Templates
import models
from db_dependency import db_dependency

router = APIRouter(prefix="/setting", tags=["setting"])
templates = Jinja2Templates(directory='templates')


@router.get('/enable', status_code=status.HTTP_201_CREATED)
async def create(
        db: db_dependency,
        enable: bool,
):
    settings = db.query(models.Setting).first()

    if settings:

        settings.Enabled = enable

    else:
        settings = models.Setting()

        db.add(settings)

    db.commit()