from pydantic import BaseModel
from pyparsing import Any
from typing import Optional

class ServerResponse(BaseModel):
    name:str
    data:Any
    status: str
    # image URL -> attribution (required by Unsplash); only set by the image endpoints
    image_credits: Optional[dict] = None
