from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
    File,
    UploadFile,
    BackgroundTasks,
)
from pydantic.main import BaseModel
from sqlalchemy.orm.session import Session
from api import schemas
from api.dependencies.auth import get_current_user
from api.dependencies.db import get_db
from api.crud import ProspectsFilesCrud, ProspectCrud
import csv, codecs, os, time
from api.core.constants import MAX_FILESIZE, MAX_ROWCOUNT, SAMPLE_ROWCOUNT

from api.models import ProspectsFiles

router = APIRouter(prefix="/api", tags=["prospects_files"])


def get_file_path(id):
    return f"./csv_store/csv_{id}.csv"


# Helper/Background task for importing prospects in route 2
def import_prospects(
    db: Session, params: schemas.CSVHeaders, file_entry: ProspectsFiles
):
    with open(get_file_path(file_entry.id), "rb") as read:
        csvtest = csv.reader(codecs.iterdecode(read, "utf-8"))
        # Skip first row if has_headers is true
        header_check = params.has_headers
        for row in csvtest:
            if header_check:
                header_check = False
                continue

            email = row[params.email_col]
            # Skip if mandatory email doesn't exist
            if(email == None or email == ""):
                continue

            first_name = ""
            if params.first_name_col != None:
                first_name = row[params.first_name_col]
            last_name = ""
            if params.last_name_col != None:
                last_name = row[params.last_name_col]
            prospect = ProspectCrud.get_prospect_by_email_user(
                db, file_entry.user_id, email
            )

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
                prospect_create = {
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                }
                ProspectCrud.create_prospect(db, file_entry.user_id, prospect_create)
                ProspectsFilesCrud.increment_processed_count(db, file_entry)

    # cleanup after import finishes, delete local csv
    os.remove(get_file_path(file_entry.id))


# Route 1
@router.post("/prospects_files", response_model=schemas.ProspectsFileUpload)
async def upload_prospects_csv(
    current_user: schemas.User = Depends(get_current_user),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    #Verify User
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )

    # Step 1: Verify CSV file, create DB entry, store it locally
    if file.content_type != "text/csv":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Please input a csv file"
        )

    # Check that file is smaller than 200 MB
    file_content = await file.read()
    if len(file_content) > MAX_FILESIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Max file size is 200 MB",
        )

    # Create entry in DB first
    file_entry = ProspectsFilesCrud.create_prospects_file(db, current_user.id, 0, 0)

    # Store first few rows of csv to return
    sample_rows = []
    # Control how many rows to add to sample
    return_row_count = SAMPLE_ROWCOUNT

    # Going to add a local folder to store csv files, rename based on db id
    # Then return sample data for column matching later if successful upload plus id of csv
    with open(get_file_path(file_entry.id), "wb+") as dest:
        dest.write(file_content)
        #Reset back to start of file before reading
        dest.seek(0)
        csvtest = csv.reader(codecs.iterdecode(dest, "utf-8"))
        row_count = 0
        for row in csvtest:
            if row_count < return_row_count:
                sample_rows.append(row)
            row_count += 1
        if row_count > MAX_ROWCOUNT:
            # cleanup first before throwing exception
            ProspectsFilesCrud.delete_prospects_file(db, file_entry.id)
            os.remove(get_file_path(file_entry.id))
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Max row count is 1,000,000",
            )
        # Updating number of rows in csv in db
        ProspectsFilesCrud.update_prospects_file(db, file_entry, row_count, 0)

    return {"id": file_entry.id, "rows": sample_rows}


# Route 2
@router.post(
    "/prospects_files/{id}/prospects", response_model=schemas.ProspectsFileImport
)
def import_csv(
    background_tasks: BackgroundTasks,
    id: int,
    params: schemas.CSVHeaders,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    #Verify User
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )

    #Check that csv wasn't already imported and the csv was deleted
    if not os.path.exists(get_file_path(id)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File already imported"
        )

    # Step 1: Get ProspectsFiles db entry, import is now async
    file_entry = ProspectsFilesCrud.get_prospects_file_by_id(db, id)

    #Verify Current User owns the requested file
    if current_user.id != file_entry.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current user does not own requested file",
        )

    background_tasks.add_task(import_prospects, db, params, file_entry)

    # Step 3: Return prospectsfile object
    return {"prospects_files": file_entry}


# Route 3
@router.get(
    "/prospects_files/{id}/progress", response_model=schemas.ProspectsFileProgress
)
def get_upload_status(
    id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    #Verify User
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )

    # Check csv_metadata table to get completed status/progress, then return info
    file_entry = ProspectsFilesCrud.get_prospects_file_by_id(db, id)

    #Verify Current User owns the requested file
    if current_user.id != file_entry.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current user does not own requested file",
        )

    return {"total": file_entry.total_rows, "processed": file_entry.processed}
