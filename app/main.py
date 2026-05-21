import logging
import time
from http import HTTPStatus

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import models
from app.api.v1.router import api_router
from app.database import Base, engine

logger = logging.getLogger("college_api")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(
    title="College Management API",
    description="A modular FastAPI app for registering students, courses, and enrollments.",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)

app.include_router(api_router, prefix="/api/v1")


def error_response(
    status_code: int,
    message: str,
    details: object | None = None,
) -> JSONResponse:
    content: dict[str, object] = {
        "error": {
            "status_code": status_code,
            "message": message,
        },
    }
    if details is not None:
        content["error"]["details"] = details

    return JSONResponse(status_code=status_code, content=content)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        process_time = time.perf_counter() - start_time
        logger.exception(
            "request failed method=%s path=%s process_time=%.4fs",
            request.method,
            request.url.path,
            process_time,
        )
        raise

    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    logger.info(
        "request completed method=%s path=%s status_code=%s process_time=%.4fs",
        request.method,
        request.url.path,
        response.status_code,
        process_time,
    )

    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    logger.warning(
        "http error method=%s path=%s status_code=%s detail=%s",
        request.method,
        request.url.path,
        exc.status_code,
        exc.detail,
    )
    response = error_response(exc.status_code, message, exc.detail)
    if exc.headers:
        response.headers.update(exc.headers)

    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    logger.warning(
        "validation error method=%s path=%s errors=%s",
        request.method,
        request.url.path,
        exc.errors(),
    )

    return error_response(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "The request data is invalid",
        exc.errors(),
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    logger.exception(
        "database error method=%s path=%s error=%s",
        request.method,
        request.url.path,
        exc,
    )

    return error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "A database error occurred while processing your request",
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "unhandled error method=%s path=%s error=%s",
        request.method,
        request.url.path,
        exc,
    )

    return error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        HTTPStatus(status.HTTP_500_INTERNAL_SERVER_ERROR).phrase,
    )


@app.get("/")
def health_check() -> dict[str, str]:
    return {"message": "College Management API is running"}
