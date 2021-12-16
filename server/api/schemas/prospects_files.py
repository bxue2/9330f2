from typing import List

from pydantic import BaseModel



class ProspectsFileUpload(BaseModel):
    id: int
    rows: List[List[str]]


class ProspectsFileImport(BaseModel):
    id: int


class ProspectsFileProgress(BaseModel):
    total: int
    processed: int
