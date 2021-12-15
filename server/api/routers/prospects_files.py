from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm.session import Session
from api import schemas
from api.dependencies.auth import get_current_user
from api.core.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from api.crud import ProspectCrud
from api.dependencies.db import get_db

router = APIRouter(prefix="/api", tags=["prospects_files"])

#1
@router.post("/prospects_files", response_model=schemas.ProspectResponse)
def upload_prospects_csv(
    current_user: schemas.User = Depends(get_current_user),
    page: int = DEFAULT_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
    db: Session = Depends(get_db),
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
    return {"id": 1, "row1": "row1", "row2": "row2"}

#2
@router.post("/prospects_files/:id/prospects", response_model=schemas.ProspectResponse)
def import_csv(
    current_user: schemas.User = Depends(get_current_user),
    page: int = DEFAULT_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
    db: Session = Depends(get_db),
):
    """Verify User"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )
    # Step 1: Parse request to get column names
    prospects = ProspectCrud.get_users_prospects(db, current_user.id, page, page_size)
    total = ProspectCrud.get_user_prospects_total(db, current_user.id)

    #Step 2: Start uploading, want this to happen async though

    # Step 3: Return id number of csv in table so we know what to track?
    return {"csvid": 1}

#3
@router.get("/prospects_files/:id/progress", response_model=schemas.ProspectResponse)
def get_upload_status(
    current_user: schemas.User = Depends(get_current_user),
    page: int = DEFAULT_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
    db: Session = Depends(get_db),
):
    """Verify User"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )

    # Check csv_metadata table to get completed status/progress, then return info

    return {"total": 1, "processed": 1}
