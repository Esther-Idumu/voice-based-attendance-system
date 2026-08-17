from pydantic import BaseModel

class StudentBase(BaseModel):
    name: str
    matric_number: str
