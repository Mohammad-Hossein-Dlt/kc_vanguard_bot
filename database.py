from sqlalchemy.sql import text
import config
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session


# ================ CREATE DATABASE IF NOT EXISTS ================
async def create_db():
    url = f"mariadb+mariadbconnector://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/"
    # URL = "postgresql://root:ZHqPsIiG4ZX9e29CkmEgoAY7@chogolisa.liara.cloud:30333/"
    sql = text("CREATE DATABASE IF NOT EXISTS %s " % config.DB_NAME)
    engine_ = create_engine(url)
    with engine_.connect() as con:
        con.execute(sql)
        con.close()
    pass


# ================================================================
DATABASE_URL = f"mariadb+mariadbconnector://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"

engine = create_engine(DATABASE_URL)

Base = declarative_base()

sessionLocal = sessionmaker(bind=engine)
