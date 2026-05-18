from pydantic import BaseModel, Field


class EnrollmentCreate(BaseModel):
    student_id: str = Field(..., min_length=1)
    course_id: str = Field(..., min_length=1)


class EnrollmentResponse(BaseModel):
    student_id: str
    course_ids: list[str]

