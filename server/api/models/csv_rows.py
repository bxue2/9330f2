from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, DateTime, Integer, String

from api.database import Base


class CsvRows(Base):
    """Contains individual rows of CSV"""

    __tablename__ = "csv_rows"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    csv_id = Column(BigInteger, ForeignKey("csv_metadata.id"))
    # Not sure if needed or if should just delete from table
    csv_string = Column(String, nullable=False)
    processed = Column(Boolean, nullable=False, default=False)

    prospect = relationship("CsvMetadata", foreign_keys=[csv_id])
