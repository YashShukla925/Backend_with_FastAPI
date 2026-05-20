from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_roles
from app.database import get_db
from app.models import User
from app.schemas.auth import UserRole
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate
from app.services import student_service
from app.services.student_service import DuplicateStudentEmailError

router = APIRouter()


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def register_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> StudentResponse:
    try:
        return student_service.create_student(db, student)
    except DuplicateStudentEmailError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email already exists",
        ) from None


@router.get("/", response_model=list[StudentResponse])
def list_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[StudentResponse]:
    return student_service.get_all_students(db)


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudentResponse:
    student = student_service.get_student_by_id(db, student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return student


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: str,
    student_update: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> StudentResponse:
    try:
        student = student_service.update_student(db, student_id, student_update)
    except DuplicateStudentEmailError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email already exists",
        ) from None

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> Response:
    deleted = student_service.delete_student(db, student_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
