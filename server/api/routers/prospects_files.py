from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile
from pydantic.main import BaseModel
from sqlalchemy.orm.session import Session
from api import schemas
from api.dependencies.auth import get_current_user
from api.dependencies.db import get_db
from api.crud import ProspectsFilesCrud, ProspectCrud
import csv, codecs, os

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
    # Reset processed count for testing purposes
    # ProspectsFilesCrud.update_prospects_file(db, file_entry, file_entry.total_rows, 0)
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
            prospect = ProspectCrud.get_prospect_by_email_user(db, file_entry.user_id, email)
            # Check if prospect already exists (by email)
            if prospect:
                # If yes, and force is true, update
                if params.force:
                    ProspectCrud.update_prospect(db, prospect, first_name, last_name)
                    ProspectsFilesCrud.increment_processed_count(db, file_entry)
                # If force is false, go to next row
                else:
                    continue
            # else create new prospect entry
            else:
                prospect_create = {'email': email, 'first_name': first_name, 'last_name': last_name}
                ProspectCrud.create_prospect(db, file_entry.user_id, prospect_create)
                ProspectsFilesCrud.increment_processed_count(db, file_entry)
    #cleanup after import finishes, delete local csv
    os.remove(f'./csv_store/csv_{file_entry.id}.csv')

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

    # Check that file is smaller than 200 MB
    # Feel like this should be checked frontend as well
    file_content = await file.read()
    if len(file_content) > 20000000:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Max file size is 200 MB"
        )

    # Create entry in DB first
    file_entry = ProspectsFilesCrud.create_prospects_file(db, current_user.id, 0, 0)

    # Going to add a local folder to store csv files, rename based on db id
    # Using id for file name to prevent duplicates, timestamps could theoretically overlap?
    with open(f'./csv_store/csv_{file_entry.id}.csv', "wb") as dest:
        dest.write(file_content)

    #Step 2: Need to return sample data for column matching later if successful upload plus id of csv
    # Need to parse first few rows of csv
    #Not sure if good practice to read file after writing, might have race conditions?
    sample_rows = []
    # control how many rows to add to sample
    return_row_count = 4
    with open(f'./csv_store/csv_{file_entry.id}.csv', "rb") as read:
        csvtest = csv.reader(codecs.iterdecode(read, 'utf-8'))
        row_count = 0
        for row in csvtest:
            if row_count < return_row_count:
                sample_rows.append(row)
            row_count += 1
        if row_count > 1000000:
            # cleanup first before throwing exception
            ProspectsFilesCrud.delete_prospects_file(db, file_entry.id)
            os.remove(f'./csv_store/csv_{file_entry.id}.csv')
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Max row count is 1,000,000"
            )
        # Updating number of rows in csv in db
        # I don't think there's a way to get the row count without reading the whole file(?)
        ProspectsFilesCrud.update_prospects_file(db, file_entry, row_count, 0)

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

    #Step 1: Get ProspectsFiles db entry, import, want this to happen async though
    file_entry = ProspectsFilesCrud.get_prospects_file_by_id(db, id)
    import_prospects(db, params, file_entry)

    # Step 3: Return prospectsfile object
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
