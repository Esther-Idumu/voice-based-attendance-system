from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)

print("students.py loaded")

@router.post("/{id}/enroll-voice")
def enroll_voice(
    id: int, 
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
    ):
    student = db.query(models.Student).filter(models.Student.id == id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    fake_embedding = [0.1, 0.2, 0.3]

    new_embedding = models.VoiceEmbedding(
        embedding=fake_embedding,
        student_id=student.id
    )

    db.add(new_embedding)
    db.commit()
    db.refresh(new_embedding)

    return {"message": "voice enrolled successfully"}