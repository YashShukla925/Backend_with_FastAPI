from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.auth import UserRole
from app.services import auth_service
from app.services.auth_service import InvalidTokenError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token_data = auth_service.decode_access_token(token)
    except InvalidTokenError:
        raise credentials_exception from None

    user = auth_service.get_user_by_id(db, token_data.user_id)
    if user is None:
        raise credentials_exception

    return user


def require_roles(*allowed_roles: UserRole) -> Callable[[User], User]:
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in {role.value for role in allowed_roles}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )

        return current_user

    return role_checker
