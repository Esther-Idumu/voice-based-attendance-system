from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import os
import uuid

from app.database import get_db
from app import models
from app.services.speaker_embedding import generate_embedding

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)

UPLOAD_DIR = "temp_audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/")
def get_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()


@router.get("/{id}")
def get_student(id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.post("/")
def create_student(name: str, matric_number: str, db: Session = Depends(get_db)):
    student = models.Student(name=name, matric_number=matric_number)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.post("/{id}/enroll-voice")
def enroll_voice(
    id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    student = db.query(models.Student).filter(models.Student.id == id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.wav")

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    embedding = generate_embedding(file_path)

    new_embedding = models.VoiceEmbedding(
        embedding=embedding,
        student_id=student.id
    )

    db.add(new_embedding)
    db.commit()

    os.remove(file_path)

    return {"message": "Voice enrolled successfully"}