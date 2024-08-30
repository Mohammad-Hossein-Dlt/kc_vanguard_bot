from typing import List

from fastapi import APIRouter, status
import models
from db_dependency import db_dependency
from utils.parse_null import parse_null
from utils.response_model import ResponseMessage

router = APIRouter(prefix="/subscriptions", tags=["Subscription"])


@router.get('/fetch_all', status_code=status.HTTP_200_OK)
async def fetch_all(
        db: db_dependency,
):

    subscriptions = db.query(models.Subscriptions).order_by(
        models.Subscriptions.OrderBy.is_(None),
        models.Subscriptions.OrderBy.asc(),
    ).all()

    return subscriptions


@router.get('/fetch_one', status_code=status.HTTP_200_OK)
async def fetch_one(
        db: db_dependency,
        subscription_id: int,
):
    subscription = db.query(models.Subscriptions).where(
        models.Subscriptions.Id == subscription_id
    ).first()

    return subscription


@router.post('/insert', status_code=status.HTTP_200_OK)
async def insert(
        db: db_dependency,
        days: int,
        total_gb: int,
        number_of_users: int,
        price: int,
):
    subscription = models.Subscriptions()

    subscription.Days = days
    subscription.Total_GB = total_gb
    subscription.Number_Of_Users = number_of_users
    subscription.Price = price

    db.add(subscription)
    db.commit()

    return {"subscription_id": subscription.Id}


@router.put('/edit', status_code=status.HTTP_200_OK)
async def edit(
        db: db_dependency,
        subscription_id: int,
        days: int | None = None,
        total_gb: int | None = None,
        number_of_users: int | None = None,
        price: int | None = None,
):
    days = parse_null(days)
    total_gb = parse_null(total_gb)
    number_of_users = parse_null(number_of_users)
    price = parse_null(price)

    subscription = db.query(models.Subscriptions).where(
        models.Subscriptions.Id == subscription_id
    ).first()

    subscription.Days = days if days is not None else subscription.Days
    subscription.Total_GB = total_gb if total_gb is not None else subscription.Total_GB
    subscription.Number_Of_Users = number_of_users if number_of_users is not None else subscription.Number_Of_Users
    subscription.Price = price if price is not None else subscription.Price

    db.commit()

    return ResponseMessage(error=False, message='subscription edited.')


@router.put("/reorder", status_code=status.HTTP_200_OK)
async def reorder(
        db: db_dependency,
        subscriptions_id: List[int],
):
    subscriptions = db.query(models.Subscriptions).all()

    for index, agent_id in enumerate(subscriptions_id):
        for agent in subscriptions:
            if agent.Id == agent_id:
                agent.OrderBy = index

    db.commit()

    return ResponseMessage(error=False, message="subscriptions reordered.")


@router.delete('/delete', status_code=status.HTTP_200_OK)
async def delete(
        db: db_dependency,
        subscription_id: int,
):
    subscription = db.query(models.Subscriptions).where(
        models.Subscriptions.Id == subscription_id,
    ).first()

    if subscription:
        db.delete(subscription)
        db.commit()

    return ResponseMessage(error=False, message="subscription deleted.")
