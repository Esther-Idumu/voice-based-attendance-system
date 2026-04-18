from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    matric_number = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))