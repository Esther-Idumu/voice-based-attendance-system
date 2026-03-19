from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

app = FastAPI()

class Student(BaseModel):
    name: str
    matric_number: str

all_students = [{"name": "Esther Idumu", "matric_number": "BU22SEN1037", "id": 1},
                {"name": "Darasimi Salau", "matric_number": "BU22SEN1002", "id": 2}]

def find_student(id):
    for student in all_students:
        if student["id"] == id:
            return student

def find_index_student(id):
    for i, student in enumerate(all_students):
        if student['id'] == id:
            return i

@app.get("/students")
def get_students():
    return{"data": all_students}

@app.post("/students", status_code=status.HTTP_201_CREATED)
def create_student(student: Student):
    student_dict = student.dict()
    student_dict['id'] = randrange(0, 100000)
    all_students.append(student_dict)
    return{"data": student_dict}

@app.get("/students/{id}")
def get_student(id: int):

    student = find_student(id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"student with id: {id} was not found")
    return {"student_detail": student}

@app.put("/students/{id}")
def update_student(id: int, student: Student):
    index = find_index_student(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"student with id: {id} does not exist")

    student_dict = student.dict()
    student_dict['id'] = id
    all_students[index] = student_dict
    return{"data": student_dict}

