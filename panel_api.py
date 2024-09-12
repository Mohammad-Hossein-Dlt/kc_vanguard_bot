import json
import uuid, secrets
from pyxui import XUI
from pyxui.errors import NotFound
from pyxui.config_gen import config_generator
from datetime import datetime, timedelta
import requests
from pyxui.errors import BadLogin
import jdatetime

xui = XUI(
    full_address='',
    panel='sanaei',
)


# ---------------------------------------------- Login

def login(
        panel_url: str,
        username: str,
        password: str,
):
    xui.full_address = panel_url
    if not xui.session_string:
        try:
            xui.login(
                username,
                password,
            )
            return True
        except BadLogin as ex:
            print(ex.message)

        return False


# ---------------------------------------------- Add Client Action

def add_client(
        panel_url: str,
        username: str,
        password: str,
        address: str,
        sni: str,
        inbound_id: int,
        ip_limit: int,
        expire_time: int,
        total_gb: int,
        client_id: str | None = None,
        email: str | None = None,
):
    response = requests.get(panel_url)

    if response.status_code != 200:
        return None, None, None
    login(panel_url, username, password)
    # ---------------------------------------------- Get Inbound
    inbounds = xui.get_inbounds()['obj']

    my_inbound = inbounds[0]
    find = False
    for i in inbounds:
        if i['id'] == inbound_id:
            my_inbound = i
            find = True
            break

    if not find:
        return None, None, None

    del my_inbound['clientStats']

    stream_settings = json.loads(my_inbound['streamSettings'])

    network = stream_settings['network']
    security = stream_settings['security']

    header_type = 'none'

    if network == 'tcp' and security == 'tls':
        header_type = 'http'

    my_inbound_id = my_inbound['id']
    port = my_inbound['port']

    # ---------------------------------------------- Create Email, Client_Id

    if not client_id:
        client_id = str(uuid.uuid4())

    if not email:
        email = secrets.token_urlsafe().replace('-', '').replace('_', '')[:8]

    # ---------------------------------------------- Add Client
    try:
        add_inbound = xui.add_client(
            inbound_id=my_inbound_id,
            uuid=client_id,
            email=email,
            enable=True,
            flow='',
            limit_ip=ip_limit,
            total_gb=total_gb,
            expire_time=expire_time,
            telegram_id='',
            subscription_id='',
        )
    except Exception as ex:
        print(ex)
        return None, None, None
    else:
        # ---------------------------------------------- Create Config String
        if add_inbound['success']:
            config = create_config_string(
                email=email,
                address=address,
                sni=sni,
                client_id=client_id,
                port=port,
                network=network,
                security=security,
                header_type=header_type,
            )
            return [config, email, client_id]
        else:
            return None, None, None


# ---------------------------------------------- Get Config

def create_config_string(
        email: str,
        address: str,
        sni: str,
        client_id: str,
        port: str,
        network: str,
        security: str,
        header_type: str,
):
    # domain = 'v1.deadlyhelios.site'

    config = {
        "ps": email,
        "add": address,
        "port": port,
        "id": client_id,
    }
    data = {
        "type": network,
        "path": '/',
        'host': address,
        'headerType': header_type,
        "security": security,
        "fp": "",  # chrome
        "alpn": "",
        "sni": sni,
    }

    generate_config = config_generator("vless", config, data)

    return generate_config


# ---------------------------------------------- Get Config Static

def get_client_info(
        panel_url: str,
        username: str,
        password: str,
        inbound_id: int,
        email: str
):
    response = requests.get(panel_url)

    if response.status_code != 200:
        return None

    login(panel_url, username, password)
    try:

        client = xui.get_client_stats(
            inbound_id=inbound_id,
            email=email,
        )

        total = client['total']
        up = client['up']
        down = client['down']
        usage = client['down'] + client['up']
        remained = total - usage
        expiry_timestamp = client['expiryTime']

        jalali_expiry_time = jdatetime.datetime.fromtimestamp(expiry_timestamp / 1000).strftime('%H:%M:%S  <-  %Y/%m/%d') if len(str(expiry_timestamp)) == 13 and expiry_timestamp > 0 else 0

        return {
            'up': up,
            'down': down,
            'usage': usage,
            'remained': remained if remained > 0 else 0,
            'total': total,
            'expired_volume': usage >= total,
            'expiry_time': jalali_expiry_time
        }
    except Exception as ex:
        print(ex)
        return None


def get_client(
        panel_url: str,
        username: str,
        password: str,
        inbound_id: int,
        email: str
):
    response = requests.get(panel_url)

    if response.status_code != 200:
        return None

    login(panel_url, username, password)
    try:

        client = xui.get_client(
            inbound_id=inbound_id,
            email=email,
        )

        return client

    except NotFound as ex:
        return None


def update_client(
        panel_url: str,
        username: str,
        password: str,
        # address: str,
        # sni: str,
        inbound_id: int,
        ip_limit: int,
        expire_time: int,
        total_gb: int,
        client_id: str,
        email: str,
):
    response = requests.get(panel_url)

    if response.status_code != 200:
        return None

    login(panel_url, username, password)
    try:

        try:
            reset = xui.request(
                path=f"{inbound_id}/resetClientTraffic/{email}",
                method="POST"
            )

            if reset.json()["success"]:

                client = xui.update_client(
                    inbound_id=inbound_id,
                    uuid=client_id,
                    email=email,
                    enable=True,
                    flow='',
                    limit_ip=ip_limit,
                    total_gb=total_gb,
                    expire_time=expire_time,
                    telegram_id='',
                    subscription_id='',
                )

                return client
            else:
                return None
        except Exception as ex:
            print(ex)
            return None

    except Exception as ex:
        print(ex)
        return None


def delete_client(
        panel_url: str,
        username: str,
        password: str,
        inbound_id: int,
        client_id: str
):
    try:
        response = requests.get(panel_url)

        if response.status_code != 200:
            return False

        login(panel_url, username, password)
        delete = xui.delete_client(
            inbound_id=inbound_id,
            uuid=client_id,
        )

        return delete['success']
    except Exception as ex:
        return False


def inbound_client_len(
        panel_url: str,
        username: str,
        password: str,
        inbound_id: int,
):
    try:
        login(panel_url, username, password)
        inbound = xui.get_inbound(inbound_id)
        settings = json.loads(inbound["obj"]["settings"])
        clients = settings["clients"]

        return len(clients)
    except Exception as ex:
        print(ex)
        return None


if __name__ == "__main__":
    info = inbound_client_len("https://v1.hyperrio.site:2088/32677b23-345a-476b-9293-124b2bdb5e89", "Hosein", "Hosein0098", 2)

    print(info)
