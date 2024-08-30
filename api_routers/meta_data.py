from fastapi import APIRouter, status
import models
from db_dependency import db_dependency

router = APIRouter(prefix="/meta_data", tags=["Meta_Data"])


@router.put('/edit', status_code=status.HTTP_200_OK)
async def edit(
        db: db_dependency,
        channel_id: str,
        bot_id: str,
        support_id: str,
):
    meta_data = db.query(models.MetaData).first()

    if meta_data:

        meta_data.Channel_Id = channel_id
        meta_data.Bot_Id = bot_id
        meta_data.Support_Id = support_id

    else:
        meta_data = models.MetaData()

        meta_data.Channel_Id = channel_id
        meta_data.Bot_Id = bot_id
        meta_data.Support_Id = support_id

        db.add(meta_data)

    db.commit()

    return 'meta_data added.'


@router.get('/fetch', status_code=status.HTTP_200_OK)
async def get(
        db: db_dependency,
):
    meta_data = db.query(models.MetaData).first()

    if meta_data:
        return meta_data

    return []


@router.delete('/delete', status_code=status.HTTP_200_OK)
async def delete(
        db: db_dependency,
        meta_data_id: int,
):
    meta_data = db.query(models.MetaData).where(
        models.MetaData.Id == meta_data_id,
    ).first()

    if meta_data:
        db.delete(meta_data)
        db.commit()

    return 'meta_data deleted.'
