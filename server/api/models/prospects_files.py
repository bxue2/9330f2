from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, DateTime, Integer

from api.database import Base


class ProspectsFiles(Base):
    """Contains metadata for CSV"""

    __tablename__ = "prospects_files"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    total_rows = Column(Integer, nullable=False)
    processed = Column(Integer, nullable=False)

    user = relationship("User", back_populates="prospects_files", foreign_keys=[user_id])
