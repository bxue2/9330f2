from sqlalchemy.orm.session import Session
from api import schemas
from api.models import ProspectsFiles

class ProspectsFilesCrud:
    @classmethod
    def get_prospects_file(
        cls,
        db: Session,
        user_id: int,
    ):
        pass

    @classmethod
    def create_prospects_file(
        cls,
        db: Session,
        user_id: int,
        total_rows: int,
        processed: int,
    ):
        file_entry = ProspectsFiles(user_id = user_id, total_rows = total_rows, processed = processed)
        db.add(file_entry)
        db.commit()
        db.refresh(file_entry)

        return file_entry

    @classmethod
    def update_prospects_file(
        cls,
        db: Session,
        user_id: int,
    ):
        pass

    @classmethod
    def delete_prospects_file(
        cls,
        db: Session,
        user_id: int,
    ):
        pass
