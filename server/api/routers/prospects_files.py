from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.param_functions import File
from pydantic.main import BaseModel
from sqlalchemy.orm.session import Session
from api import schemas
from api.dependencies.auth import get_current_user
from api.crud import ProspectCrud
from api.dependencies.db import get_db

router = APIRouter(prefix="/api", tags=["prospects_files"])

#Request body for route 1
class CSVFile(BaseModel):
    file: File

#Request body for route 2
class CSVHeaders(BaseModel):
    email_col: int
    first_name_col: int = None
    last_name_col: int = None
    force: bool
    has_headers: bool

#1
@router.post("/prospects_files", response_model=schemas.ProspectsFileUpload)
def upload_prospects_csv(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    csv: CSVFile
):
    """Verify User"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )

    #Step 1: Store CSV file somehow?
    # Create entry in DB first
    # Going to add a local folder to store csv files, rename based on db id


    #Step 2: Need to return sample data for column matching later if successful upload plus id of csv
    return {"id": 1, "rows": "row1"}

#2
@router.post("/prospects_files/{id}/prospects", response_model=schemas.ProspectsFileImport)
def import_csv(
    current_user: schemas.User = Depends(get_current_user),
    id: int,
    db: Session = Depends(get_db),
):
    """Verify User"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )
    # Step 1: Parse request to get column names
    print(id)
    # prospects = ProspectCrud.get_users_prospects(db, current_user.id, page, page_size)
    # total = ProspectCrud.get_user_prospects_total(db, current_user.id)

    #Step 2: Start uploading, want this to happen async though

    # Step 3: Return id number of csv in table so we know what to track? doc mentions prospectsfile object?
    return {"csvid": 1}

#3
@router.get("/prospects_files/{id}/progress", response_model=schemas.ProspectsFileProgress)
def get_upload_status(
    current_user: schemas.User = Depends(get_current_user),
    id: int,
    db: Session = Depends(get_db),
):
    """Verify User"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )

    # Check csv_metadata table to get completed status/progress, then return info

    return {"total": 1, "processed": 1}
