import time
from datetime import datetime

import pytz
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import models
from database import engine, create_db
from database import sessionLocal
from sqlalchemy import or_
from api_routers import (
    message,
    settings,
    server,
    inbound,
    test_inbound,
    subscription,
    payment,
    config,
    user,
    meta_data,
)
import threading

from panel_api import get_client_info, get_client


def delete_state():
    db = sessionLocal()

    time_now = datetime.now(pytz.UTC)

    junk_users_tasks = db.query(models.UsersTasks).where(
        models.UsersTasks.ExpirationDate < time_now
    ).all()

    for i in junk_users_tasks:
        db.delete(i)

    db.commit()
    db.close()


def delete_failed_payments():
    db = sessionLocal()

    failed_payments = db.query(models.Payments).where(
        or_(
            models.Payments.Status == False,
            # models.Payments.Ref_Id == None,
        )
    )

    for i in failed_payments:
        db.delete(i)

    db.commit()

    db.close()


def do_update():
    while True:
        delete_failed_payments()
        delete_state()
        time.sleep(10)


def set_stats():
    db = sessionLocal()

    services = db.query(
        models.UsersServices,
        models.Inbounds,
    ).join(
        models.Inbounds
    ).all()

    for i in services:
        service = i[0]
        the_inbound = i[1]
        the_server = db.query(models.Servers).where(
            models.Servers.Id == the_inbound.Server_Id
        ).first()

        try:
            if get_client(
                    panel_url=the_server.Url,
                    username=the_server.UserName,
                    password=the_server.Password,
                    inbound_id=the_inbound.Panel_Inbound_Id,
                    email=service.Email,
            ):

                status = get_client_info(
                    panel_url=the_server.Url,
                    username=the_server.UserName,
                    password=the_server.Password,
                    inbound_id=the_inbound.Panel_Inbound_Id,
                    email=service.Email,
                )

                if status:

                    service.Remained = status["remained"]
        except Exception as ex:
            pass

    db.commit()
    db.close()


def set_stats_update():
    while True:
        set_stats()
        time.sleep(10)


def start_update():
    threading.Thread(target=do_update).start()

    threading.Thread(target=set_stats_update).start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Start up.")
    await create_db()
    models.Base.metadata.create_all(bind=engine)
    start_update()
    yield
    print("Shout down.")


app = FastAPI(lifespan=lifespan)

origins = [
    'https://www.google.com',
    'https://sandbox.zarinpal.com',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

BASE_URL = "/api/v2"

app.include_router(message.router, prefix=BASE_URL)
app.include_router(settings.router, prefix=BASE_URL)
app.include_router(server.router, prefix=BASE_URL)
app.include_router(inbound.router, prefix=BASE_URL)
app.include_router(test_inbound.router, prefix=BASE_URL)
app.include_router(subscription.router, prefix=BASE_URL)
app.include_router(payment.router, prefix=BASE_URL)
app.include_router(config.router, prefix=BASE_URL)
app.include_router(user.router, prefix=BASE_URL)
app.include_router(meta_data.router, prefix=BASE_URL)


if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=8000)

