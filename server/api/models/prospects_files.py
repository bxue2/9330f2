from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, DateTime, Integer

from api.database import Base


class ProspectsFiles(Base):
    """Contains metadata for CSV"""

    __tablename__ = "prospects_files"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    # maybe add link to user table?
    user_id = Column(BigInteger, nullable=False)
    total_rows = Column(Integer, nullable=False)
    processed = Column(Integer, nullable=False)
