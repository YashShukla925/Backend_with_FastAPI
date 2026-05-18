from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Course
from app.schemas.course import CourseCreate, CourseUpdate


class DuplicateCourseNameError(Exception):
    pass


def create_course(db: Session, course: CourseCreate) -> Course:
    existing_course = get_course_by_name(db, course.name)
    if existing_course is not None:
        raise DuplicateCourseNameError

    created_course = Course(**course.model_dump())
    db.add(created_course)
    db.commit()
    db.refresh(created_course)
    return created_course


def get_all_courses(db: Session) -> list[Course]:
    return list(db.scalars(select(Course)).all())


def get_course_by_id(db: Session, course_id: str) -> Course | None:
    return db.get(Course, course_id)


def get_course_by_name(db: Session, name: str) -> Course | None:
    return db.scalar(select(Course).where(Course.name == name))


def update_course(
    db: Session,
    course_id: str,
    course_update: CourseUpdate,
) -> Course | None:
    course = get_course_by_id(db, course_id)
    if course is None:
        return None

    update_data = course_update.model_dump(exclude_unset=True)
    new_name = update_data.get("name")
    if new_name is not None:
        existing_course = get_course_by_name(db, new_name)
        if existing_course is not None and existing_course.id != course_id:
            raise DuplicateCourseNameError

    for field, value in update_data.items():
        setattr(course, field, value)

    db.commit()
    db.refresh(course)
    return course


def delete_course(db: Session, course_id: str) -> bool:
    course = get_course_by_id(db, course_id)
    if course is None:
        return False

    db.delete(course)
    db.commit()
    return True
