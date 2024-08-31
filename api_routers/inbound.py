from fastapi import APIRouter, status

import constants
import models
from db_dependency import db_dependency
from panel_api import inbound_client_len
from utils.parse_null import parse_null
from utils.response_model import ResponseMessage

router = APIRouter(prefix="/inbound", tags=["Inbound"])


@router.get('/fetch_all', status_code=status.HTTP_200_OK)
async def fetch_all(
        db: db_dependency,
        server_id: int,
):
    server = db.query(models.Servers).where(
        models.Servers.Id == server_id
    ).first()

    inbounds = db.query(models.Inbounds).where(
        models.Inbounds.Server_Id == server_id,
    ).order_by(
        models.Inbounds.OrderBy.is_(None),
        models.Inbounds.OrderBy.asc(),
    ).all()

    for i in inbounds:
        i.Length = inbound_client_len(server.Url, server.UserName, server.Password, i.Panel_Inbound_Id)

    return inbounds


@router.get('/fetch_one', status_code=status.HTTP_200_OK)
async def fetch_one(
        db: db_dependency,
        inbound_id: int,
):
    server, inbound = db.query(models.Servers, models.Inbounds).join(
        models.Inbounds
    ).where(
        models.Inbounds.Id == inbound_id
    ).first()

    inbound.Length = inbound_client_len(server.Url, server.UserName, server.Password, inbound.Panel_Inbound_Id)

    return inbound


@router.post('/insert', status_code=status.HTTP_200_OK)
async def insert(
        db: db_dependency,
        remark: str,
        server_id: int,
        address: str,
        sni: str,
        panel_inbound_id: int,
        port: int,
        network: constants.Network,
        security: constants.Security,
):
    inbound = models.Inbounds()

    inbound.Remark = remark
    inbound.Server_Id = server_id
    inbound.Address = address
    inbound.Sni = sni
    inbound.Panel_Inbound_Id = panel_inbound_id
    inbound.Inbound_Port = port
    inbound.Network = network
    inbound.Security = security

    header_type = constants.HeaderType.none
    # if network == 'tcp' and security == 'tls':
    if network == constants.Network.tcp and security == constants.Security.tls:
        header_type = constants.HeaderType.http

    inbound.HeaderType = header_type

    db.add(inbound)
    db.commit()

    return 'inbound added.'


@router.put('/edit', status_code=status.HTTP_200_OK)
async def edit(
        db: db_dependency,
        inbound_id: int,
        remark: str | None = None,
        server_id: int | None = None,
        address: str | None = None,
        sni: str | None = None,
        panel_inbound_id: int | None = None,
        port: int | None = None,
        network: constants.Network | None = None,
        security: constants.Security | None = None,
        limit: int | None = None,
):
    remark = parse_null(remark)
    server_id = parse_null(server_id)
    address = parse_null(address)
    sni = parse_null(sni)
    panel_inbound_id = parse_null(panel_inbound_id)
    port = parse_null(port)
    network = parse_null(network)
    security = parse_null(security, constants.Security.none)
    limit = parse_null(limit)

    inbound = db.query(models.Inbounds).where(
        models.Inbounds.Id == inbound_id,
    ).first()

    header_type = constants.HeaderType.none
    if network == constants.Network.tcp and security == constants.Security.tls:
        header_type = constants.HeaderType.http

    inbound.Remark = remark if remark is not None else inbound.Remark
    inbound.Server_Id = server_id if server_id is not None else inbound.Server_Id
    inbound.Address = address if address is not None else inbound.Address
    inbound.Sni = sni if sni is not None else inbound.Sni
    inbound.Panel_Inbound_Id = panel_inbound_id if panel_inbound_id is not None else inbound.Panel_Inbound_Id
    inbound.Inbound_Port = port if port is not None else inbound.Inbound_Port
    inbound.Network = network if network is not None else inbound.Network
    inbound.Security = security if security is not None else inbound.Security
    inbound.HeaderType = header_type if network is not None and security is not None else inbound.HeaderType
    inbound.Limit = limit if limit is not None else inbound.Limit

    db.commit()

    return 'inbound added.'


@router.put("/reorder", status_code=status.HTTP_200_OK)
async def reorder(
        db: db_dependency,
        server_id: int,
        inbounds_id: list[int],
):
    get_inbounds = db.query(models.Inbounds).where(
        models.Inbounds.Server_Id == server_id,
    ).all()

    print(get_inbounds)

    for index, inbound_id in enumerate(inbounds_id):
        for inbound in get_inbounds:
            if inbound.Id == inbound_id:
                inbound.OrderBy = index

    db.commit()

    return ResponseMessage(error=False, message="inbounds reordered.")


@router.delete('/delete', status_code=status.HTTP_200_OK)
async def delete(
        db: db_dependency,
        inbound_id: int,
):
    inbound = db.query(models.Inbounds).where(
        models.Inbounds.Id == inbound_id,
    ).first()

    if inbound:
        db.delete(inbound)
        db.commit()

    return 'server deleted.'
