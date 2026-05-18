from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.course import CourseCreate, CourseResponse, CourseUpdate
from app.services import course_service
from app.services.course_service import DuplicateCourseNameError

router = APIRouter()


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def register_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
) -> CourseResponse:
    try:
        return course_service.create_course(db, course)
    except DuplicateCourseNameError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A course with this name already exists",
        ) from None


@router.get("/", response_model=list[CourseResponse])
def list_courses(db: Session = Depends(get_db)) -> list[CourseResponse]:
    return course_service.get_all_courses(db)


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: str,
    db: Session = Depends(get_db),
) -> CourseResponse:
    course = course_service.get_course_by_id(db, course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    return course


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: str,
    course_update: CourseUpdate,
    db: Session = Depends(get_db),
) -> CourseResponse:
    try:
        course = course_service.update_course(db, course_id, course_update)
    except DuplicateCourseNameError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A course with this name already exists",
        ) from None

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: str,
    db: Session = Depends(get_db),
) -> Response:
    deleted = course_service.delete_course(db, course_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
