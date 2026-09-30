# main.py
from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models.student import Student
from schemas.student import StudentCreate, StudentUpdate, StudentPatch, StudentResponse

Base.metadata.create_all(bind=engine)  # creates tables that don't exist yet

app = FastAPI()

# Helper functions 
def get_student_or_404(student_id: int, db: Session) -> Student:  # find a student or stop with 404 code
    student = db.get(Student, student_id)  # look up by primary key
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


def email_taken(db: Session, email: str, exclude_id: int | None = None) -> bool:  # True if another student has this email
    stmt = select(Student).where(Student.email == email)
    if exclude_id is not None:
        stmt = stmt.where(Student.id != exclude_id)  # ignore the student being updated
    return db.scalars(stmt).first() is not None

# CRUD Functions
@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    if email_taken(db, student.email):
        raise HTTPException(status_code=409, detail="Email already registered")  # 409 = conflict (e.g. duplicate email)

    new_student = Student(**student.model_dump())  # turn the schema into a database object
    db.add(new_student)       # stage it
    db.commit()               # save it
    db.refresh(new_student)   # reload it so it has its new id
    return new_student


@app.get("/students", response_model=list[StudentResponse])
def list_students(
    major: str | None = None,  # optional filter: ?major=CS
    min_gpa: float | None = Query(default=None, ge=0.0, le=4.0),  # optional filter: ?min_gpa=3.0
    db: Session = Depends(get_db),
):
    stmt = select(Student)  # start with all students
    if major is not None:
        stmt = stmt.where(Student.major == major)
    if min_gpa is not None:
        stmt = stmt.where(Student.gpa >= min_gpa)
    return db.scalars(stmt).all()


@app.get("/students/{student_id}", response_model=StudentResponse)  
def get_student(student_id: int, db: Session = Depends(get_db)):  # get one student by id
    return get_student_or_404(student_id, db)  # helper function returns the student or raises 404


@app.put("/students/{student_id}", response_model=StudentResponse)
def replace_student(student_id: int, data: StudentUpdate, db: Session = Depends(get_db)):  # full replacement
    student = get_student_or_404(student_id, db)  # helper function returns the student or raises 404

    if email_taken(db, data.email, exclude_id=student_id):  # ignore this student's own email
        raise HTTPException(status_code=409, detail="Email already registered")

    for key, value in data.model_dump().items():  # every field gets updated, including ones not sent
        setattr(student, key, value)

    db.commit()
    db.refresh(student)
    return student


@app.patch("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, data: StudentPatch, db: Session = Depends(get_db)):  # partial update
    student = get_student_or_404(student_id, db)  # helper function returns the student or raises 404

    updates = data.model_dump(exclude_unset=True)  # only the fields the user actually sent

    for field in ("name", "email"):
         # edge case: name and email can be left out, but not set to null
         # required in the database, so they can't be set to null
        if field in updates and updates[field] is None:
            raise HTTPException(status_code=422, detail=f"{field} cannot be null")

    if "email" in updates and email_taken(db, updates["email"], exclude_id=student_id):
        raise HTTPException(status_code=409, detail="Email already registered")

    for key, value in updates.items():  # only sent fields get updated, the rest stay the same
        setattr(student, key, value)

    db.commit()
    db.refresh(student)
    return student


@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):  # delete a student
    student = get_student_or_404(student_id, db)  # helper function returns the student or raises 404
    db.delete(student)  # mark it for deletion
    db.commit()         # save the change
    return {"message": f"Student {student_id} deleted successfully"}

