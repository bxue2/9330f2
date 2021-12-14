from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger, DateTime, Integer

from api.database import Base


class CsvMetadata(Base):
    """Contains metadata for CSV"""

    __tablename__ = "csv_metadata"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    progress = Column(Integer)
