from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Student
from app.schemas.student import StudentCreate, StudentUpdate


class DuplicateStudentEmailError(Exception):
    pass


def create_student(db: Session, student: StudentCreate) -> Student:
    existing_student = get_student_by_email(db, student.email)
    if existing_student is not None:
        raise DuplicateStudentEmailError

    created_student = Student(**student.model_dump())
    db.add(created_student)
    db.commit()
    db.refresh(created_student)
    return created_student


def get_all_students(db: Session) -> list[Student]:
    return list(db.scalars(select(Student)).all())


def get_paginated_students(
    db: Session,
    page: int,
    page_size: int,
) -> tuple[list[Student], int]:
    offset = (page - 1) * page_size
    total_items = db.scalar(select(func.count()).select_from(Student)) or 0
    students = list(
        db.scalars(
            select(Student)
            .order_by(Student.name, Student.id)
            .offset(offset)
            .limit(page_size),
        ).all(),
    )

    return students, total_items


def get_student_by_id(db: Session, student_id: str) -> Student | None:
    return db.get(Student, student_id)


def get_student_by_email(db: Session, email: str) -> Student | None:
    return db.scalar(select(Student).where(Student.email == email))


def update_student(
    db: Session,
    student_id: str,
    student_update: StudentUpdate,
) -> Student | None:
    student = get_student_by_id(db, student_id)
    if student is None:
        return None

    update_data = student_update.model_dump(exclude_unset=True)
    new_email = update_data.get("email")
    if new_email is not None:
        existing_student = get_student_by_email(db, new_email)
        if existing_student is not None and existing_student.id != student_id:
            raise DuplicateStudentEmailError

    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student


def delete_student(db: Session, student_id: str) -> bool:
    student = get_student_by_id(db, student_id)
    if student is None:
        return False

    db.delete(student)
    db.commit()
    return True
