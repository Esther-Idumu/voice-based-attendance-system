from sqlalchemy import Column, Date, Integer, String, Boolean, ForeignKey, JSON, DateTime, Table
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime, date

from .database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    matric_number = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    embeddings = relationship("VoiceEmbedding", back_populates="student",cascade="all, delete")
    attendances = relationship("Attendance", backref="student")
    courses = relationship("Course", secondary="student_courses", back_populates="students")

class VoiceEmbedding(Base):
    __tablename__ = "voice_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    embedding = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    student = relationship("Student", back_populates="embeddings")

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    attendance_date = Column(Date, default=date.today)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    attendances = relationship("Attendance", backref="course")
    students = relationship("Student", secondary="student_courses", back_populates="courses")

student_courses = Table(
    "student_courses",
    Base.metadata,
    Column("student_id", ForeignKey("students.id")),
    Column("course_id", ForeignKey("courses.id"))
)