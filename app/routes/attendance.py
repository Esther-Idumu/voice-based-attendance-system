from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import uuid
import numpy as np

from app.database import get_db
from app import models
from app.services.audio_converter import convert_to_wav
from app.services.speaker_embedding import generate_embedding
from datetime import date, datetime
from app import models
from app.services.transcription import transcribe_audio
import time 

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)

UPLOAD_DIR = "temp_audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


@router.post("/verify")
def verify_voice(
    course_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    total_start = time.time()
    extension = os.path.splitext(file.filename)[1]

    file_path = os.path.join(
        UPLOAD_DIR,
        f"{uuid.uuid4()}{extension}"
    )

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    conversion_start = time.time()
    wav_path = convert_to_wav(file_path)
    conversion_time = time.time() - conversion_start


    course = db.query(models.Course).filter(
        models.Course.id == course_id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    transcription_start = time.time()
    transcribed_text = transcribe_audio(wav_path)
    transcription_time = time.time() - transcription_start

    print("TRANSCRIBED:", transcribed_text)
    print(f"Transcription Time: {transcription_time:.3f} seconds")
    print(f"Conversion Time: {conversion_time:.3f} seconds")

    if "present" not in transcribed_text:
        os.remove(file_path)
        return {
            "status": "failed",
            "reason": "invalid_speech",
            "message": "You must say 'present'"
        }

    verification_start = time.time()
    input_embedding = generate_embedding(
        wav_path,
        source="VERIFICATION"
        )
    
    verification_time = time.time() - verification_start
    print(f"Speaker Verification Time: {verification_time:.3f} seconds")
    print("Input embedding length:", len(input_embedding))
    os.remove(file_path)

    if os.path.exists(file_path):
        os.remove(file_path)

    if os.path.exists(wav_path):
        os.remove(wav_path)

    embeddings = db.query(models.VoiceEmbedding).all()
    print(f"Embeddings found: {len(embeddings)}")

    if not embeddings:
        raise HTTPException(status_code=404, detail="No embeddings found")

    student_embeddings = {}

    for emb in embeddings:
        student_embeddings.setdefault(emb.student_id, []).append(emb.embedding)

    best_student_id = None
    highest_score = -1

    for student_id, emb_list in student_embeddings.items():
        student_best_score = -1

        for emb in emb_list:
            if len(emb) != len(input_embedding):
                continue

            print("Stored embedding length:", len(emb))

            score = cosine_similarity(input_embedding, emb)

            print(
                f"Student {student_id} similarity: {score}"
            )

            if score > student_best_score:
                student_best_score = score

        if student_best_score > highest_score:
            highest_score = student_best_score
            best_student_id = student_id
            print("Current best:", best_student_id)

    THRESHOLD = 0.40

    print("Highest score:", highest_score)
    print("Best student:", best_student_id)
    
    if highest_score < THRESHOLD:
        return {
            "status": "failed",
            "reason": "no_match",
            "message": "No matching student",
            "score": float(highest_score)
        }

    student = db.query(models.Student).filter(
        models.Student.id == best_student_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if course_id not in [c.id for c in student.courses]:
        raise HTTPException(
            status_code=403,
            detail="Student not enrolled in this course"
        )

    today = date.today()

    existing_attendance = db.query(models.Attendance).filter(
        models.Attendance.student_id == best_student_id,
        models.Attendance.course_id == course_id,
        models.Attendance.attendance_date == today
    ).first()

    if existing_attendance:
        return {
            "status": "failed",
            "reason": "already_marked",
            "message": "Attendance already marked for this course today",
            "student_id": best_student_id
        }

    attendance_start = time.time()
    new_attendance = models.Attendance(
        student_id=best_student_id,
        course_id=course_id,
        attendance_date=today,
        timestamp=datetime.utcnow()
    )

    db.add(new_attendance)
    db.commit()

    attendance_time = time.time() - attendance_start

    print(
        f"Attendance Marking Time: "
        f"{attendance_time:.3f} seconds"
    )

    total_time = time.time() - total_start

    print(
        f"TOTAL PROCESSING TIME: "
        f"{total_time:.3f} seconds"
    )

    return {
        "status": "success",
        "student_id": student.id,
        "name": student.name,
        "similarity": highest_score,
        "message": "Attendance marked successfully",

        "audio_conversion_time": round(conversion_time, 3),
        "transcription_time": round(transcription_time, 3),
        "speaker_verification_time": round(verification_time, 3),
        "attendance_marking_time": round(attendance_time, 3),
        "total_time": round(total_time, 3)
    }

