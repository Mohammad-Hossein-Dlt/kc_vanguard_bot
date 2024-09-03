from fastapi import APIRouter, HTTPException, status

import models
from db_dependency import db_dependency
from utils.parse_null import parse_null
from utils.response_model import ResponseMessage

router = APIRouter(prefix="/server", tags=["Server"])


@router.get('/fetch_all', status_code=status.HTTP_200_OK)
async def fetch_all(
        db: db_dependency,
):
    inbounds = db.query(models.Servers).order_by(
        models.Servers.OrderBy.is_(None),
        models.Servers.OrderBy.asc(),
    ).all()

    return inbounds


@router.get('/fetch_one', status_code=status.HTTP_200_OK)
async def fetch_one(
        db: db_dependency,
        server_id: int,
):
    inbound = db.query(models.Servers).where(
        models.Servers.Id == server_id,
    ).first()

    return inbound


@router.post('/insert', status_code=status.HTTP_200_OK)
async def insert(
        db: db_dependency,
        url: str,
        remark: str,
        username: str,
        password: str
):
    server = models.Servers()

    server.Url = url
    server.Remark = remark
    server.UserName = username
    server.Password = password

    db.add(server)
    db.commit()

    return {"server_id": server.Id}


@router.put('/edit', status_code=status.HTTP_200_OK)
async def edit(
        db: db_dependency,
        server_id: int,
        url: str | None = None,
        remark: str | None = None,
        username: str | None = None,
        password: str | None = None,
):
    url = parse_null(url)
    remark = parse_null(remark)
    username = parse_null(username)
    password = parse_null(password)

    server = db.query(models.Servers).where(
        models.Servers.Id == server_id,
    ).first()

    server.Url = url if url is not None else server.Url
    server.Remark = remark if remark is not None else server.Remark
    server.UserName = username if username is not None else server.UserName
    server.Password = password if password is not None else server.Password

    db.commit()

    return ResponseMessage(error=False, message="server updated.")


@router.put("/reorder", status_code=status.HTTP_200_OK)
async def reorder(
        db: db_dependency,
        servers_id: list[int],
):
    servers = db.query(models.Servers).all()

    for index, server_id in enumerate(servers_id):
        for server in servers:
            if server.Id == server_id:
                server.OrderBy = index

    db.commit()

    return ResponseMessage(error=False, message="servers reordered.")


@router.delete('/delete', status_code=status.HTTP_200_OK)
async def delete(
        db: db_dependency,
        server_id: int,
):
    server = db.query(models.Servers).where(
        models.Servers.Id == server_id,
    ).first()

    if server:
        db.delete(server)
        db.commit()

    return ResponseMessage(error=False, message="server deleted.")
