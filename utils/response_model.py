from pydantic import BaseModel


class ResponseMessage(BaseModel):
    error: bool = True
    message: str = "an error occurred!"
