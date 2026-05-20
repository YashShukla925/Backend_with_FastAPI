import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.auth import TokenData, UserCreate, UserRole

SECRET_KEY = "change-this-secret-key-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
PASSWORD_HASH_ITERATIONS = 100_000


class DuplicateUserEmailError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_HASH_ITERATIONS,
    ).hex()
    return f"pbkdf2_sha256${salt}${password_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        algorithm, salt, stored_hash = hashed_password.split("$", 2)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_HASH_ITERATIONS,
    ).hex()
    return hmac.compare_digest(password_hash, stored_hash)


def create_user(db: Session, user: UserCreate) -> User:
    existing_user = get_user_by_email(db, user.email)
    if existing_user is not None:
        raise DuplicateUserEmailError

    created_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hash_password(user.password),
        role=user.role.value,
    )
    db.add(created_user)
    db.commit()
    db.refresh(created_user)
    return created_user


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError

    return user


def create_access_token(user: User) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    payload = {
        "sub": user.id,
        "role": user.role,
        "exp": int(expires_at.timestamp()),
    }
    return _encode_jwt(payload)


def decode_access_token(token: str) -> TokenData:
    try:
        payload = _decode_jwt(token)
        user_id = payload.get("sub")
        role = payload.get("role")
        if user_id is None or role is None:
            raise InvalidTokenError

        return TokenData(user_id=user_id, role=UserRole(role))
    except ValueError:
        raise InvalidTokenError from None


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _base64url_decode(data: str) -> bytes:
    padded_data = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded_data.encode("ascii"))


def _encode_jwt(payload: dict[str, object]) -> str:
    header = {"alg": ALGORITHM, "typ": "JWT"}
    encoded_header = _base64url_encode(
        json.dumps(header, separators=(",", ":")).encode("utf-8"),
    )
    encoded_payload = _base64url_encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8"),
    )
    signing_input = f"{encoded_header}.{encoded_payload}"
    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_base64url_encode(signature)}"


def _decode_jwt(token: str) -> dict[str, object]:
    encoded_header, encoded_payload, encoded_signature = token.split(".")
    signing_input = f"{encoded_header}.{encoded_payload}"
    expected_signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()

    if not hmac.compare_digest(
        _base64url_encode(expected_signature),
        encoded_signature,
    ):
        raise ValueError

    header = json.loads(_base64url_decode(encoded_header))
    if header.get("alg") != ALGORITHM:
        raise ValueError

    payload = json.loads(_base64url_decode(encoded_payload))
    expires_at = payload.get("exp")
    if not isinstance(expires_at, int):
        raise ValueError

    if datetime.now(timezone.utc).timestamp() >= expires_at:
        raise ValueError

    return payload
