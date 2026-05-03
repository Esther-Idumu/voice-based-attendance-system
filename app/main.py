from fastapi import FastAPI

from . import models
from .database import engine, get_db
from app.routes import students, attendance, courses

# Create database tables 
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Register routers  
app.include_router(students.router)
app.include_router(attendance.router)
app.include_router(courses.router)
