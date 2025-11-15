from pydantic import BaseModel
from pyparsing import Any

class ServerResponse(BaseModel):
    name:str
    data:Any
    status: str
