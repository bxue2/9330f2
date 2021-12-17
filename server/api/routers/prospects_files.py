from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile
from pydantic.main import BaseModel
from sqlalchemy.orm.session import Session
from api import schemas
from api.dependencies.auth import get_current_user
from api.dependencies.db import get_db
from api.crud import ProspectsFilesCrud, ProspectCrud
import shutil, csv, codecs

from api.models import ProspectsFiles

router = APIRouter(prefix="/api", tags=["prospects_files"])

#Request body for route 2
class CSVHeaders(BaseModel):
    email_col: int
    first_name_col: int = None
    last_name_col: int = None
    force: bool = False
    has_headers: bool = False

#Helper for importing prospects in route 2
def import_prospects(db: Session, params: CSVHeaders, file_entry: ProspectsFiles):
    with open(f'./csv_store/csv_{file_entry.id}.csv', "rb") as read:
        csvtest = csv.reader(codecs.iterdecode(read, 'utf-8'))
        #Skip first row if has_headers is true
        header_check = params.has_headers
        for row in csvtest:
            if header_check:
                header_check = False
                continue

            email = row[params.email_col]
            first_name = ""
            if(params.first_name_col != None):
                first_name = row[params.first_name_col]
            last_name = ""
            if(params.last_name_col != None):
                last_name = row[params.last_name_col]
            print(params.first_name_col)
            print(row)
            prospect = ProspectCrud.get_prospect_by_email_user(db, file_entry.user_id, email)
            print(prospect)
            # Check if prospect already exists (by email)
            if prospect:
                # If yes, and force is true, update
                if params.force:
                    ProspectCrud.update_prospect(db, prospect, first_name, last_name)
                # If force is false, continue
                else:
                    continue
            # else create new prospect entry
            else:

                prospect_create = {'email': email, 'first_name': first_name, 'last_name': last_name}
                ProspectCrud.create_prospect(db, file_entry.user_id, prospect_create)

    #cleanup after import finishes?

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

    #Step 1: Verify CSV file, create DB entry, store it locally
    if(file.content_type != 'text/csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Please input a csv file"
        )

    # Create entry in DB first
    file_entry = ProspectsFilesCrud.create_prospects_file(db, current_user.id, 0, 0)

    print(file_entry.id)
    # Going to add a local folder to store csv files, rename based on db id
    with open(f'./csv_store/csv_{file_entry.id}.csv', "wb") as dest:
        shutil.copyfileobj(file.file, dest)

    #Step 2: Need to return sample data for column matching later if successful upload plus id of csv
    # Need to parse first few rows of csv
    #Not sure if good practice to read file after writing, might have race conditions?
    sample_rows = []
    with open(f'./csv_store/csv_{file_entry.id}.csv', "rb") as read:
        csvtest = csv.reader(codecs.iterdecode(read, 'utf-8'))
        row_count = 0
        for row in csvtest:
            # control how many rows to add to sample
            if row_count < 4:
                sample_rows.append(row)
            row_count += 1
        # Updating number of rows in csv in db
        # I don't think there's a way to get the row count without reading the whole file(?)
        ProspectsFilesCrud.update_prospects_file(db, file_entry, row_count, 0)
        # file_entry.total_rows = row_count
        # try:
        #     db.commit()
        # except Exception as e:
        #     raise HTTPException(status_code=503, detail="Could not connect to db")

    # Had difficulties directly converting file to something parsable
    # csvread = csv.reader(codecs.iterdecode(file.file, 'utf-8'))
    # print(csvread)
    # for row in csvread:
    #     print(row[0])

    return {"id": file_entry.id, "rows": sample_rows}

#2
@router.post("/prospects_files/{id}/prospects", response_model=schemas.ProspectsFileImport)
def import_csv(
    current_user: schemas.User = Depends(get_current_user),
    id: int = 0,
    db: Session = Depends(get_db),
    params: CSVHeaders = None,
):
    """Verify User"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )
    # Step 1: Parse request to get column names
    print(id)
    print(params.email_col)
    # prospects = ProspectCrud.get_users_prospects(db, current_user.id, page, page_size)
    # total = ProspectCrud.get_user_prospects_total(db, current_user.id)

    #Step 2: Start uploading, want this to happen async though
    file_entry = ProspectsFilesCrud.get_prospects_file_by_id(db, id)

    import_prospects(db, params, file_entry)

    # Step 3: Return prospectsfile object?
    return {"prospects_files": file_entry}

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
    file_entry = ProspectsFilesCrud.get_prospects_file_by_id(db, id)

    return {"total": file_entry.total_rows, "processed": file_entry.processed}
