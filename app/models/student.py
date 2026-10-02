# models/student.py
from sqlalchemy import String, Float, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.database import Base



class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    major: Mapped[str | None] = mapped_column(String(100), nullable=True)
    gpa: Mapped[float | None] = mapped_column(Float, nullable=True)

    __table_args__ = (  # rules for the whole table
        CheckConstraint("gpa >= 0.0 AND gpa <= 4.0", name="check_gpa_range"), # SQL rule
    )

    @validates("gpa") # Python rule: runs whenever a gpa is assigned
    def validate_gpa(self, key, value):
        if value is not None and not (0.0 <= value <= 4.0): # GPA rule
            raise ValueError("GPA must be between 0.0 and 4.0")
        return value # whatever is returned gets saved as the gpa

    def __repr__(self):
        return f"<Student {self.id}: {self.name} ({self.email})>"