from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


def generate_uuid() -> str:
    return str(uuid4())


class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    age = Column(Integer, nullable=False)

    enrollments = relationship(
        "Enrollment",
        back_populates="student",
        cascade="all, delete-orphan",
    )


class Course(Base):
    __tablename__ = "courses"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(String(500), nullable=False)
    duration = Column(String(50), nullable=False)

    enrollments = relationship(
        "Enrollment",
        back_populates="course",
        cascade="all, delete-orphan",
    )


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_student_course"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False, index=True)
    course_id = Column(String, ForeignKey("courses.id"), nullable=False, index=True)

    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
