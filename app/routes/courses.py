from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)

@router.post("/")
def create_course(name: str, db: Session = Depends(get_db)):
    course = models.Course(name=name)
    db.add(course)
    db.commit()
    db.refresh(course)

    return course


@router.get("/")
def get_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).all()