from sqlalchemy.orm.session import Session
from api import schemas
from api.models import ProspectsFiles


class ProspectsFilesCrud:
    @classmethod
    def get_prospects_file_by_id(cls, db: Session, id: int):
        file_entry = db.query(ProspectsFiles).get(id)

        return file_entry

    @classmethod
    def create_prospects_file(
        cls,
        db: Session,
        user_id: int,
        total_rows: int,
        processed: int,
    ):
        file_entry = ProspectsFiles(
            user_id=user_id, total_rows=total_rows, processed=processed
        )
        db.add(file_entry)
        db.commit()
        db.refresh(file_entry)

        return file_entry

    # Assumes you use get_prospects_file() before calling this so you can pass it in
    # Need to verify matching user id's before calling this
    @classmethod
    def update_prospects_file(
        cls,
        db: Session,
        file_entry: ProspectsFiles,
        total_rows: int,
        processed: int,
    ):
        file_entry.total_rows = total_rows
        file_entry.processed = processed
        db.commit()
        db.refresh(file_entry)
        return file_entry

    @classmethod
    def increment_processed_count(cls, db: Session, file_entry: ProspectsFiles):
        file_entry.processed += 1
        db.commit()
        db.refresh(file_entry)
        return file_entry

    @classmethod
    def delete_prospects_file(cls, db: Session, id: int):
        file_entry = db.query(ProspectsFiles).get(id)
        db.delete(file_entry)
        db.commit()
