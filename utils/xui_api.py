import secrets
from datetime import datetime, timedelta

import requests
import uuid
import json
import base64
from urllib.parse import urlencode

from constants import gb_size
# from pyxui import XUI
# from pyxui.errors import BadLogin
#
# xui = XUI(
#     full_address='',
#     panel='sanaei',
# )
#
#
# def login(
#         panel_url: str,
#         username: str,
#         password: str,
# ):
#     xui.full_address = panel_url
#     if not xui.session_string:
#         try:
#             xui.login(
#                 username,
#                 password,
#             )
#             return True
#         except BadLogin as ex:
#             print(ex.message)
#
#         return False
#
#
# log = login(
#     "https://v1.hyperrio.site:2088/32677b23-345a-476b-9293-124b2bdb5e89",
#     "Hosein",
#     "Hosein0098"
# )
#
# print(log)

# class Exceptions(Exception):
#     def __init__(self, message, error_code):
#         self.message = message
#         self.error_code = error_code
#
#
# class NotFound(Exceptions):
#     code = 'NOT_FOUND'
#     message = 'Error 404 has been received'
#
#     def __init__(self):
#         super().__init__(self.message, self.code)
#
#     def __str__(self):
#         return f"[{self.code}] {self.message}."
#
#
# def config_generator(protocol: str, config=dict, data: dict = None) -> str:
#     if protocol == "vmess":
#         config = "vmess://" + base64.b64encode(json.dumps(config).encode('utf-8')).decode('utf-8')
#
#     elif protocol == "vless":
#         config = "vless://{}@{}:{}?{}#{}".format(config['id'], config['add'], config['port'], urlencode(data),
#                                                  config['ps'])
#     return config
#
#
# class PanelApi:
#
#     def __init__(self, panel_url, username, password):
#         self.panel_url = panel_url
#         self.username = username
#         self.password = password
#
#         self.session = requests.Session()
#         self.is_login = False
#
#     def verify_request(self, request: requests.Response):
#
#         data = request.json()
#
#         if request.status_code == 200 and data["success"]:
#             return data
#
#         raise NotFound()
#
#     def check_access(self):
#         response = requests.get(self.panel_url)
#         if response.status_code == 200 and self.is_login:
#             return True
#         return False
#
#     def login(self):
#         login_url = self.panel_url + "/login"
#
#         login_data = {
#             "username": self.username,
#             "password": self.password,
#         }
#         login_response = self.session.post(login_url, json=login_data)
#         if login_response.status_code != 404:
#             print(login_response.text)
#             self.is_login = True
#             return login_response.json()
#
#         raise NotFound()
#
#     def get_inbounds(self):
#
#         if not self.check_access():
#             raise NotFound()
#
#         get_inbound_url = self.panel_url + f"/panel/api/inbounds/list"
#
#         inbound = self.session.get(get_inbound_url)
#
#         data = inbound.json()
#
#         if inbound.status_code == 200 and data["success"]:
#             return data
#
#         raise NotFound()
#
#     def get_inbound(self, inbound_id):
#
#         if not self.check_access():
#             raise NotFound()
#
#         get_inbound_url = self.panel_url + f"/panel/api/inbounds/get/{inbound_id}"
#
#         inbound = self.session.get(get_inbound_url)
#
#         data = inbound.json()
#
#         if inbound.status_code == 200 and data["success"]:
#             return data
#
#         raise NotFound()
#
#     def get_data_from_inbound(self, inbound_id):
#         try:
#             if not self.check_access():
#                 raise NotFound()
#
#             inbound = self.get_inbound(inbound_id)['obj']
#
#             print(inbound)
#
#             stream_settings = json.loads(inbound['streamSettings'])
#
#             network = stream_settings['network']
#             security = stream_settings['security']
#
#             header_type = 'none'
#
#             if network == 'tcp' and security == 'tls':
#                 header_type = 'http'
#
#             the_inbound_id = inbound['id']
#             port = inbound['port']
#
#             print(the_inbound_id, port, network, security, header_type)
#             return the_inbound_id, port, network, security, header_type
#         except Exception as ex:
#             raise NotFound()
#
#     def add_client(
#             self,
#             address: str,
#             sni: str,
#             inbound_id: int,
#             ip_limit: int,
#             days: int,
#             total_gb: int,
#     ):
#         if not self.check_access():
#             raise NotFound()
#
#         try:
#             the_inbound_id, port, network, security, header_type = self.get_data_from_inbound(inbound_id)
#         except Exception as ex:
#             raise NotFound()
#
#         client_id = str(uuid.uuid4())
#         email = secrets.token_urlsafe().replace('-', '').replace('_', '')[:16]
#
#         expire_time = datetime.now() + timedelta(days=days)
#
#         setting = {
#
#             "clients": [
#                 {
#                     "id": client_id,
#                     "email": email,
#                     "enable": "true",
#                     "flow": "",
#                     "limitIp": ip_limit,
#                     "totalGB": total_gb * gb,
#                     "expiryTime": int(expire_time.timestamp() * 1000) if total_gb != 0 else 0,
#                     "tgId": "",
#                     "subId": "",
#                 }
#             ],
#         }
#
#         data = {
#             "id": inbound_id,
#             "settings": json.dumps(setting)
#         }
#
#         add_url = self.panel_url + "/panel/api/inbounds/addClient"
#
#         add_client_response = self.session.post(add_url, json=data)
#
#         if add_client_response.status_code == 200 and self.update_client(
#                 client_id,
#                 email,
#                 inbound_id,
#                 ip_limit,
#                 days,
#                 total_gb,
#         ):
#             config = {
#                 "ps": email,
#                 "add": address,
#                 "port": port,
#                 "id": client_id,
#             }
#             data = {
#                 "type": network,
#                 "path": '/',
#                 'host': address,
#                 'headerType': header_type,
#                 "security": security,
#                 "fp": "",  # chrome
#                 "alpn": "",
#                 "sni": sni,
#             }
#             return config_generator("vless", config, data)
#
#     def update_client(
#             self,
#             client_id,
#             email,
#             inbound_id: int,
#             ip_limit: int,
#             days: int,
#             total_gb: int,
#     ):
#         if not self.check_access():
#             raise NotFound()
#
#         expire_time = datetime.now() + timedelta(days=days)
#
#         setting = {
#
#             "clients": [
#                 {
#                     "id": client_id,
#                     "email": email,
#                     "enable": "true",
#                     "flow": "",
#                     "limitIp": ip_limit,
#                     "totalGB": total_gb * gb,
#                     "expiryTime": int(expire_time.timestamp() * 1000) if total_gb != 0 else 0,
#                     "tgId": "",
#                     "subId": "",
#                 }
#             ],
#         }
#
#         data = {
#             "id": inbound_id,
#             "settings": json.dumps(setting)
#         }
#
#         add_url = self.panel_url + f"/panel/api/inbounds/updateClient/{client_id}"
#
#         update_client_response = self.session.post(add_url, json=data)
#         data = update_client_response.json()
#         if update_client_response.status_code == 200 and data["success"]:
#             print(data)
#             return True
#
#         raise NotFound()
#
#     def get_client(
#             self,
#             inbound_id,
#             client_id,
#             email,
#     ):
#         get_inbounds = self.get_inbounds()
#
#         if not email and not client_id:
#             raise ValueError()
#
#         for inbound in get_inbounds['obj']:
#             if inbound['id'] != inbound_id:
#                 continue
#
#             settings = json.loads(inbound['settings'])
#
#             for client in settings['clients']:
#                 if client['email'] != email and client['id'] != client_id:
#                     continue
#
#                 return client
#
#         raise NotFound()
#
#     def get_client_stats(
#             self,
#             inbound_id,
#             email,
#     ):
#         get_inbounds = self.get_inbounds()
#
#         if not email:
#             raise ValueError()
#
#         for inbound in get_inbounds['obj']:
#             if inbound['id'] != inbound_id:
#                 continue
#
#             client_stats = inbound['clientStats']
#
#             for client in client_stats:
#                 if client['email'] != email:
#                     continue
#
#                 return client
#
#         raise NotFound()
#
#     def delete_client(
#             self,
#             inbound_id,
#             client_id,
#     ):
#         delete_url = self.panel_url + f"/panel/api/inbounds/{inbound_id}/delClient/{client_id}"
#         delete_response = self.session.post(delete_url)
#         data = delete_response.json()
#         if delete_response.status_code == 200 and data["success"]:
#             return data
#
#         raise NotFound()
#
#
# xui = PanelApi(
#     "https://v1.hyperrio.site:2088/32677b23-345a-476b-9293-124b2bdb5e89",
#     "Hosein",
#     "Hosein0098",
# )

# xui.login()

# print(
#     xui.delete_client(
#         7,
#         "7b78007b-5baf-4be5-9f27-c0c8303c795d",
#     )
# )

# print(
#     xui.add_client(
#         "v1.hyperrio.site",
#         "v1.hyperrio.site",
#         7,
#         0,
#         30,
#         10,
#     ),
# )

# print(
#     xui.update_client(
#         "9025339d-6bc9-4700-8ae7-8bb0b200d11e",
#         "VYF176oAXvODHW3d",
#         7,
#         0,
#         40,
#         20,
#     ),
# )

# print(
#     xui.get_client_stats(
#         7,
#         "VYF176oAXvODHW3d"
#     )
# )
