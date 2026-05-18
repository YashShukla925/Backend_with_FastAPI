from fastapi import FastAPI

from app.api.v1.router import api_router
from app.database import Base, engine
from app import models

app = FastAPI(
    title="College Management API",
    description="A modular FastAPI app for registering students, courses, and enrollments.",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def health_check() -> dict[str, str]:
    return {"message": "College Management API is running"}
