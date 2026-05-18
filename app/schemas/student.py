from pydantic import BaseModel, ConfigDict, EmailStr, Field


class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=1, le=120)


class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    age: int | None = Field(default=None, ge=1, le=120)


class StudentResponse(StudentCreate):
    id: str

    model_config = ConfigDict(from_attributes=True)
