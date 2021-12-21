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

# Request body for route 2
class CSVHeaders(BaseModel):
    email_col: int
    first_name_col: int = None
    last_name_col: int = None
    force: bool = False
    has_headers: bool = False
