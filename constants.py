import enum

kb_size = 1024
mb_size = kb_size ** 2
gb_size = kb_size ** 3


def data_size(size_in_bytes):
    size_in_bytes = int(size_in_bytes)
    in_kb = size_in_bytes / kb_size
    in_mb = size_in_bytes / mb_size
    in_gb = size_in_bytes / gb_size

    if size_in_bytes < kb_size:
        return f'{size_in_bytes:0.2f} بایت'
    if size_in_bytes < mb_size:
        return f'{in_kb:0.2f} کیلوبایت'
    if size_in_bytes < gb_size:
        return f'{in_mb:0.2f} مگابایت'
    else:
        return f'{in_gb:0.2f} گیگ'


persian_number = {
    1: "یک",
    2: "دو",
    3: "سه",
    4: "چهار",
    5: "پنج",
    6: "شش",
    7: "هفت",
    8: "هشت",
    9: "نه",
    10: "ده",
    11: "یازده",
    12: "دوازده",
}


def get_persian_number(number: int):
    try:
        return persian_number[number]
    except:
        return str(None)


class Network(str, enum.Enum):
    ws = "ws"
    tcp = "tcp"


class Security(str, enum.Enum):
    tls = "tls"
    none = "none"


class HeaderType(str, enum.Enum):
    http = "http"
    none = "none"


class UserWalletPlusOrMinus(str, enum.Enum):
    plus = "plus"
    minus = "minus"


class UserTask(str, enum.Enum):
    buy = "buy"
    wallet = "wallet"
    free_test = "free_test"
    service_management = "service_management"
