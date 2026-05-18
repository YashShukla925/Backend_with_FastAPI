from fastapi import APIRouter

from app.api.v1.routers import courses, enrollments, students

api_router = APIRouter()
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(courses.router, prefix="/courses", tags=["Courses"])
api_router.include_router(enrollments.router, prefix="/enrollments", tags=["Enrollments"])

