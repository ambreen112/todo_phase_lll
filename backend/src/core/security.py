"""Security utilities for authentication and authorization."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import bcrypt
from fastapi import HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel

from .config import get_settings


class TokenData(BaseModel):
    """Token payload data."""

    user_id: UUID
    email: str
    exp: Optional[datetime] = None


class PasswordHasher:
    """Password hashing using bcrypt."""

    def __init__(self, rounds: int = 12):
        self.rounds = rounds

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        try:
            password_bytes = plain_password.encode("utf-8")
            hashed_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False


class JWTTokenManager:
    """JWT token generation and verification."""

    def __init__(self):
        self.settings = get_settings()
        self.hasher = PasswordHasher()

    def create_access_token(
        self, user_id: UUID, email: str, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a new JWT access token."""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.settings.access_token_expire_minutes
            )

        to_encode = {
            "sub": str(user_id),
            "email": email,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }

        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.jwt_secret_key,
            algorithm=self.settings.algorithm,
        )
        return encoded_jwt

    def verify_token(self, token: str) -> TokenData:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret_key,
                algorithms=[self.settings.algorithm],
            )
            user_id = payload.get("sub")
            email = payload.get("email")

            if user_id is None or email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing claims",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return TokenData(user_id=UUID(user_id), email=email, exp=payload.get("exp"))

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )


# Global instances
password_hasher = PasswordHasher()
jwt_manager = JWTTokenManager()
