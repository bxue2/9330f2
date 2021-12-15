from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, DateTime, Integer

from api.database import Base


class ProspectsFiles(Base):
    """Contains metadata for CSV"""

    __tablename__ = "csv_metadata"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    total_rows = Column(Integer, nullable=False)
    processed = Column(Integer, nullable=False)
    #Not sure if completed needed, could just compare processed and total_rows
    completed = Column(Boolean, nullable=False)
