from datetime import datetime
from typing import List

from pydantic import BaseModel
from pydantic.networks import EmailStr


class ProspectsUpload(BaseModel):
    id: int
    rows: str[][]


class ProspectCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class ProspectResponse(BaseModel):
    """One page of prospects"""

    prospects: List[Prospect]
    size: int
    total: int
