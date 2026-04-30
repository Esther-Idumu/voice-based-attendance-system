from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import uuid
import numpy as np

from app.database import get_db
from app import models
from app.services.speaker_embedding import generate_embedding

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
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.wav")

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    input_embedding = generate_embedding(file_path)

    os.remove(file_path)

    embeddings = db.query(models.VoiceEmbedding).all()

    if not embeddings:
        raise HTTPException(status_code=404, detail="No embeddings found")

    best_match = None
    highest_score = -1

    for emb in embeddings:
        score = cosine_similarity(input_embedding, emb.embedding)

        if score > highest_score:
            highest_score = score
            best_match = emb

    THRESHOLD = 0.75

    if highest_score < THRESHOLD:
        return {
            "message": "No matching student",
            "score": float(highest_score)
        }

    student = db.query(models.Student).filter(
        models.Student.id == best_match.student_id
    ).first()

    return {
        "student_id": student.id,
        "name": student.name,
        "similarity": float(highest_score)
    }