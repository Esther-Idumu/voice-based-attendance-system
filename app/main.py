from fastapi import FastAPI

app = FastAPI()

@app.get("/students")
def get_students():
    return{"message": "Student name is..."}

@app.get("/students{id}")
def get_student():
    return{"message": "A single student name is..."}

@app.post("/students")
def save_students():
    return{"message": "Save this student"}