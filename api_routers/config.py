from fastapi import APIRouter, Request, status
from fastapi.templating import Jinja2Templates
import models
from constants import data_size
from db_dependency import db_dependency

from panel_api import get_client_info, add_client
from utils.expire_time import expiration_time

router = APIRouter(prefix="/config", tags=["config"])
templates = Jinja2Templates(directory='templates')


@router.get('/create', status_code=status.HTTP_201_CREATED)
async def create(
        db: db_dependency,
        inbound_id: int,
        ip_limit: int,
        days: int,
        total_gb: int,
):
    server, inbound = db.query(models.Servers, models.Inbounds).select_from(
        models.Inbounds
    ).filter(
        models.Inbounds.Id == inbound_id,
    ).first()

    expire_time, raw_time = expiration_time(days=days)

    if server:
        return add_client(
            panel_url=server.Url,
            username=server.UserName,
            password=server.Password,
            address=inbound.Address,
            sni=inbound.Sni,
            inbound_id=inbound.Panel_Inbound_Id,
            ip_limit=ip_limit,
            expire_time=expire_time,
            total_gb=total_gb,
        )

    return None


@router.get('/information', status_code=status.HTTP_200_OK)
async def information(
        db: db_dependency,
        request: Request,
        service_id: int,
):
    user_services, user, subscription, inbound = db.query(
        models.UsersServices,
        models.Users,
        models.Subscriptions,
        models.Inbounds
    ).join(
        models.Users
    ).join(
        models.Subscriptions
    ).join(
        models.Inbounds
    ).where(
        models.UsersServices.Id == service_id
    ).first()

    server = db.query(models.Servers).where(
        models.Servers.Id == inbound.Server_Id
    ).first()

    config_status = get_client_info(
        panel_url=server.Url,
        username=server.UserName,
        password=server.Password,
        inbound_id=inbound.Panel_Inbound_Id,
        email=user_services.Email,
    )

    if config_status:

        context = {
            'request': request,
            'usage': data_size(config_status['usage']),
            'remained': data_size(config_status['remained']),
            'total': data_size(config_status['total']),
            'expiry_time': config_status['expiry_time'],
        }

        if user_services and user and subscription and inbound:
            return templates.TemplateResponse(name='config_information.html', context=context)

    else:
        return None
