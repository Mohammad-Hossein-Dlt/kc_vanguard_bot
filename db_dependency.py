from fastapi import Depends
from database import *
from typing import Annotated


def get_db():
    db = sessionLocal()
    try:
        print("111111")
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
