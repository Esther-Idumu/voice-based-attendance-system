from fastapi import APIRouter, Depends, HTTPException
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


@router.post("/enroll")
def enroll_student(
    student_id: int,
    course_id: int,
    db: Session = Depends(get_db)
):
    student = db.query(models.Student).filter(
        models.Student.id == student_id
    ).first()

    course = db.query(models.Course).filter(
        models.Course.id == course_id
    ).first()

    if not student or not course:
        raise HTTPException(status_code=404, detail="Student or Course not found")

    # prevent duplicate enrollment
    if course in student.courses:
        return {"message": "Student already enrolled in this course"}

    student.courses.append(course)

    db.commit()

    return {
        "message": f"Student {student.name} enrolled in {course.name}"
    }