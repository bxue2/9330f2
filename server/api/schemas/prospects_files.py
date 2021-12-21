from typing import List

from pydantic import BaseModel


class ProspectsFiles(BaseModel):
    id: int
    user_id: int
    total_rows: int
    processed: int

    class Config:
        orm_mode = True


class ProspectsFileUpload(BaseModel):
    id: int
    rows: List[List[str]]


class ProspectsFileImport(BaseModel):
    prospects_files: ProspectsFiles


class ProspectsFileProgress(BaseModel):
    total: int
    processed: int
