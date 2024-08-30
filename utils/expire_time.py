from datetime import datetime, timedelta


def expiration_time(days: int):
    expire_time = datetime.now() + timedelta(days=days)
    return int(expire_time.timestamp() * 1000), expire_time
