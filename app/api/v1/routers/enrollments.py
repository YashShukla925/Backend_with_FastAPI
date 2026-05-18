from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.enrollment import EnrollmentCreate, EnrollmentResponse
from app.services import enrollment_service

router = APIRouter()


@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll_student(
    enrollment: EnrollmentCreate,
    db: Session = Depends(get_db),
) -> EnrollmentResponse:
    created_enrollment = enrollment_service.enroll_student_in_course(db, enrollment)
    if created_enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student or course not found",
        )

    return created_enrollment


@router.get("/students/{student_id}", response_model=EnrollmentResponse)
def get_student_enrollments(
    student_id: str,
    db: Session = Depends(get_db),
) -> EnrollmentResponse:
    enrollment = enrollment_service.get_courses_for_student(db, student_id)
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return enrollment


@router.get("/courses/{course_id}", response_model=list[str])
def get_course_enrollments(
    course_id: str,
    db: Session = Depends(get_db),
) -> list[str]:
    student_ids = enrollment_service.get_students_for_course(db, course_id)
    if student_ids is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    return student_ids
