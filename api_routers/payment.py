from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.templating import Jinja2Templates
import models
from config import API_TOKEN
from db_dependency import db_dependency
from suds.client import Client
from fastapi.responses import RedirectResponse
from telegram import Bot

router = APIRouter(prefix="/payment", tags=["payment"])

bot = Bot(token=API_TOKEN)

templates = Jinja2Templates(directory='templates')

ZARINPAL_MERCHANT_ID = "75218ab1-d6a0-4548-bd36-f819e26c306c"

# ZARINPAL_WEBSERVICE_URL = "https://sandbox.zarinpal.com/pg/services/WebGate/wsdl"
# ZARINPAL_PAYMENT_URL = "https://sandbox.zarinpal.com/pg/StartPay/"


ZARINPAL_WEBSERVICE_URL = "https://zarinpal.com/pg/services/WebGate/wsdl"
ZARINPAL_PAYMENT_URL = "https://zarinpal.com/pg/StartPay/"


@router.get("/request")
async def request_payment(
        db: db_dependency,
        request: Request,
        user_id: int,
        payment_id: str,
        amount: int,
):
    payment = db.query(models.Payments).where(
        models.Payments.Payment_Id == payment_id
    ).first()

    if payment:
        return RedirectResponse(url=f"{ZARINPAL_PAYMENT_URL}{payment.Authority}", status_code=307)

    client = Client(ZARINPAL_WEBSERVICE_URL)

    base = request.url.scheme + "://" + request.url.netloc
    path_parts = request.url.path.split("/")
    prefix = "/".join(path_parts[0:-1])
    if not prefix.startswith("/"):
        prefix = "/" + prefix
    callback_url = base + prefix + "/" + "verify" + f"?payment_id={payment_id}"

    result = client.service.PaymentRequest(
        MerchantID=ZARINPAL_MERCHANT_ID,
        Amount=amount,
        Description="description",
        CallbackURL=callback_url
    )

    if result.Status == 100:
        payment_url = f"{ZARINPAL_PAYMENT_URL}{result.Authority}"

        user = db.query(models.Users).where(
            models.Users.Chat_Id == user_id
        ).first()

        payment = models.Payments()

        payment.User_Id = user.Id
        payment.Payment_Id = payment_id
        payment.Authority = result.Authority
        payment.Amount = amount

        db.add(payment)
        db.commit()

        return RedirectResponse(url=payment_url, status_code=307)
    else:
        raise HTTPException(status_code=400, detail=result.Status)


@router.get("/verify")
async def verify_payment(
        db: db_dependency,
        request: Request,
        payment_id: str,
        Authority: str,
        Status: str,
):
    context = {
        "request": request,
    }

    payment = db.query(models.Payments).where(
        models.Payments.Payment_Id == payment_id
    ).first()

    if Status != "OK":
        if not payment.Ref_Id:
            payment.Status = False
            db.commit()
        return templates.TemplateResponse(name="unsuccessful_payment.html", context=context)

    client = Client(ZARINPAL_WEBSERVICE_URL)

    result = client.service.PaymentVerification(
        MerchantID=ZARINPAL_MERCHANT_ID,
        Authority=Authority,
        Amount=payment.Amount
    )

    if result.Status == 100:

        payment.Ref_Id = result.RefID
        payment.Status = True

        user = db.query(models.Users).where(
            models.Users.Id == payment.User_Id
        ).first()

        user.Wallet += payment.Amount

        db.commit()

        await bot.send_message(
            chat_id=user.Chat_Id,
            text=f" مبلغ {payment.Amount} تومان پرداخت شد و رقم آن به کیف پول شما اضافه شد ",
        )

        context["ref_id"] = result.RefID
        return templates.TemplateResponse(name="successful_payment.html", context=context)
    else:
        return templates.TemplateResponse(name="unsuccessful_payment.html", context=context)
