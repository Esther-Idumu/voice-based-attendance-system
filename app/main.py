from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2 
from psycopg2.extras import RealDictCursor 
from sqlalchemy.orm import Session
import time 
from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Establish a connection to the database 
while True:
    try: 
        conn = psycopg2.connect(host='localhost', database='voice_attendance_system', user='postgres', password='potatoes', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful!")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2)

# Get all the students from the database
@app.get("/students")
def get_students(db: Session = Depends(get_db)):
    students = db.query(models.Student).all()
    return{"data": students}

# Create a student in the database 
@app.post("/students", status_code=status.HTTP_201_CREATED)
def create_student(student: schemas.StudentBase, db: Session = Depends(get_db)):
  new_student = models.Student(**student.dict())
  db.add(new_student)
  db.commit()
  db.refresh(new_student)
  
  return{"data": new_student}

# Get a student from the database 
@app.get("/students/{id}")
def get_student(id: int, db: Session = Depends(get_db)):

    student = db.query(models.Student).filter(models.Student.id == id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"student with id: {id} was not found")
    return {"student_detail": student}

# @app.put("/students/{id}")
# def update_student(id: int, updated_student: schemas.StudentBase, db: Session = Depends(get_db)):
#     student_query = db.query(models.Student).filter(models.Student.id == id)
#     student = student_query.first()

#     if student == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"student with id: {id} does not exist")

#     student_query.update(update_student.dict(), synchronize_session=False)

#     db.commit()
#     return{"data": student_query.first()}

