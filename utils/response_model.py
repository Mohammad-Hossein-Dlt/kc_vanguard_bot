from pydantic import BaseModel
from typing import Any


class ResponseMessage(BaseModel):
    error: bool = True
    message: Any = "an error occurred!"
