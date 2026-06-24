from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
import os
import uuid
import time

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
def create_student(name: str = Form(...), matric_number: str = Form(...), db: Session = Depends(get_db)):
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
    enrollment_start = time.time()
    student = db.query(models.Student).filter(
        models.Student.id == id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    from app.services.audio_converter import convert_to_wav

    # Keep original extension
    extension = os.path.splitext(file.filename)[1]

    file_path = os.path.join(
        UPLOAD_DIR,
        f"{uuid.uuid4()}{extension}"
    )

    wav_path = None

    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # Convert to wav
        conversion_start = time.time()
        wav_path = convert_to_wav(file_path)

        conversion_time = time.time() - conversion_start
        print(f"Conversion Time: {conversion_time:.3f} seconds")
        print(f"WAV path: {wav_path}")
        print(f"Exists: {os.path.exists(wav_path)}")
        print(f"Size: {os.path.getsize(wav_path)} bytes")

        # Generate embedding
        embedding_start = time.time()
        embedding = generate_embedding(
            wav_path,
            source="ENROLLMENT"
            )
        embedding_time = time.time() - embedding_start
        print(
            f"Enrollment Embedding Time: "
            f"{embedding_time:.3f} seconds"
        )

        # Save embedding
        new_embedding = models.VoiceEmbedding(
            embedding=embedding,
            student_id=student.id
        )

        db_start = time.time()
        db.add(new_embedding)
        db.commit()
        db.refresh(new_embedding)

        db_time = time.time() - db_start

        print(
            f"Enrollment Database Save Time: "
            f"{db_time:.3f} seconds")
        
        total_enrollment_time = time.time() - enrollment_start

        print(
            f"TOTAL ENROLLMENT TIME: "
            f"{total_enrollment_time:.3f} seconds")

        return {
            "message": "Voice enrolled successfully",
            "student_id": student.id
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        # Delete original uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete converted wav file
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)