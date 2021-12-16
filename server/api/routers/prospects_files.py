from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile
from pydantic.main import BaseModel
from sqlalchemy.orm.session import Session
from api import schemas
from api.dependencies.auth import get_current_user
from api.crud import ProspectCrud
from api.dependencies.db import get_db
import shutil, csv, codecs

from api.models import ProspectsFiles

router = APIRouter(prefix="/api", tags=["prospects_files"])

#Request body for route 2
class CSVHeaders(BaseModel):
    email_col: int
    first_name_col: int = None
    last_name_col: int = None
    force: bool
    has_headers: bool

#1
@router.post("/prospects_files", response_model=schemas.ProspectsFileUpload)
async def upload_prospects_csv(
    current_user: schemas.User = Depends(get_current_user),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Verify User"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )

    #Step 1: Store CSV file somehow?
    # Create entry in DB first
    file_entry = ProspectsFiles(user_id= current_user.id, total_rows = 0, processed = 0)
    db.add(file_entry)
    try:
        db.commit()
    except Exception as e:
        print(e)
        #return a 400 here

    # Going to add a local folder to store csv files, rename based on db id
    with open(f'./csv_store/csv_{file_entry.id}.csv', "wb") as dest:
        shutil.copyfileobj(file.file, dest)

    #Step 2: Need to return sample data for column matching later if successful upload plus id of csv
    # Need to parse first few rows of csv
    #Not sure if good practice to read file after writing, might have race conditions?
    sample_rows = []
    with open("./csv_store/dest_csv.csv", "rb") as read:
        csvtest = csv.reader(codecs.iterdecode(read, 'utf-8'))
        row_count = 0
        for row in csvtest:
            # control how many rows to add to sample
            if row_count < 4:
                sample_rows.append(row)
            row_count += 1
        # Updating number of rows in csv in db
        # I don't think there's a way to get the row count without reading the whole file(?)
        file_entry.total_rows = row_count
        #might need try catch here
        db.commit()

    # Had difficulties directly converting file to something parsable
    # csvread = csv.reader(codecs.iterdecode(file.file, 'utf-8'))
    # print(csvread)
    # for row in csvread:
    #     print(row[0])

    return {"id": 1, "rows": sample_rows}

#2
@router.post("/prospects_files/{id}/prospects", response_model=schemas.ProspectsFileImport)
def import_csv(
    current_user: schemas.User = Depends(get_current_user),
    id: int = 0,
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
    id: int = 0,
    db: Session = Depends(get_db),
):
    """Verify User"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )

    # Check csv_metadata table to get completed status/progress, then return info

    return {"total": 1, "processed": 1}
