from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse
from app.services import auth_service
from app.services.auth_service import DuplicateUserEmailError, InvalidCredentialsError

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    try:
        return auth_service.create_user(db, user)
    except DuplicateUserEmailError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        ) from None


@router.post("/login", response_model=Token)
def login_user(
    credentials: UserLogin,
    db: Session = Depends(get_db),
) -> Token:
    try:
        user = auth_service.authenticate_user(
            db,
            credentials.email,
            credentials.password,
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    return Token(access_token=auth_service.create_access_token(user))


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)) -> UserResponse:
    return current_user
