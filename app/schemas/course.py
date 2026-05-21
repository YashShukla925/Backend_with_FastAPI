from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pagination import PaginationMeta


class CourseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    duration: str = Field(..., min_length=1, max_length=50)


class CourseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=500)
    duration: str | None = Field(default=None, min_length=1, max_length=50)


class CourseResponse(CourseCreate):
    id: str

    model_config = ConfigDict(from_attributes=True)


class PaginatedCourseResponse(BaseModel):
    items: list[CourseResponse]
    meta: PaginationMeta
