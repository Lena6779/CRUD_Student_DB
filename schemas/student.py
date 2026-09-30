# schemas/student.py
from pydantic import BaseModel, ConfigDict, Field


class StudentBase(BaseModel):  # shared fields, not used directly in routes and other schemas inherit them 
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=120)
    major: str | None = Field(default=None, max_length=100)
    gpa: float | None = Field(default=None, ge=0.0, le=4.0)


class StudentCreate(StudentBase):  # POST: data for a new student
    pass # same fields as StudentBase 


class StudentUpdate(StudentBase):  # PUT: full replacement
    pass # same fields as StudentBase 


class StudentPatch(BaseModel):  # PATCH: partial update, every field optional
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: str | None = Field(default=None, min_length=3, max_length=120)
    major: str | None = Field(default=None, max_length=100)
    gpa: float | None = Field(default=None, ge=0.0, le=4.0)


class StudentResponse(StudentBase):  # what the API sends back
    id: int # added by the database

    model_config = ConfigDict(from_attributes=True)  # lets Pydantic read SQLAlchemy objects, not just dicts