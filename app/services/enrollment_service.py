from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Enrollment
from app.schemas.enrollment import EnrollmentCreate, EnrollmentResponse
from app.services.course_service import get_course_by_id
from app.services.student_service import get_student_by_id


def enroll_student_in_course(
    db: Session,
    enrollment: EnrollmentCreate,
) -> EnrollmentResponse | None:
    student = get_student_by_id(db, enrollment.student_id)
    course = get_course_by_id(db, enrollment.course_id)

    if student is None or course is None:
        return None

    existing_enrollment = db.scalar(
        select(Enrollment).where(
            Enrollment.student_id == enrollment.student_id,
            Enrollment.course_id == enrollment.course_id,
        )
    )
    if existing_enrollment is None:
        db.add(
            Enrollment(
                student_id=enrollment.student_id,
                course_id=enrollment.course_id,
            )
        )
        db.commit()

    return get_courses_for_student(db, enrollment.student_id)


def get_courses_for_student(db: Session, student_id: str) -> EnrollmentResponse | None:
    student = get_student_by_id(db, student_id)
    if student is None:
        return None

    course_ids = db.scalars(
        select(Enrollment.course_id).where(Enrollment.student_id == student_id)
    ).all()
    return EnrollmentResponse(student_id=student_id, course_ids=sorted(course_ids))


def get_students_for_course(db: Session, course_id: str) -> list[str] | None:
    course = get_course_by_id(db, course_id)
    if course is None:
        return None

    student_ids = db.scalars(
        select(Enrollment.student_id).where(Enrollment.course_id == course_id)
    ).all()
    return sorted(student_ids)
