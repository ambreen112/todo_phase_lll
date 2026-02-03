"""API dependencies for authentication and authorization."""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Header, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from src.core.security import jwt_manager, TokenData
from src.models.database import get_session
from src.models.user import User
from src.models.schemas import ErrorResponse


security = HTTPBearer()


async def get_current_user(
    request: Request,
    auth: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    """
    Get the current authenticated user from JWT token.

    Args:
        request: FastAPI request object for debugging
        auth: Bearer token from Authorization header (automatic from FastAPI)

    Returns:
        TokenData with user_id and email

    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    token = auth.credentials

    try:
        token_data = jwt_manager.verify_token(token)
        return token_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> Optional[TokenData]:
    """
    Get the current user if authenticated, None otherwise.

    Args:
        authorization: Bearer token from Authorization header

    Returns:
        TokenData if authenticated, None otherwise
    """
    if not authorization:
        return None

    if not authorization.startswith("Bearer "):
        return None

    token = authorization[7:]

    try:
        return jwt_manager.verify_token(token)
    except Exception:
        return None


async def verify_user_owns_resource(
    user_id: UUID,
    current_user: TokenData = Depends(get_current_user),
) -> UUID:
    """
    Verify that the authenticated user owns the requested resource.

    Args:
        user_id: The user_id from the URL path
        current_user: The authenticated user from JWT

    Returns:
        The user_id if ownership is verified

    Raises:
        HTTPException: If user_id doesn't match authenticated user
    """
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource",
        )
    return user_id


async def get_user_by_id(
    user_id: UUID,
    session: Session = Depends(get_session),
) -> User:
    """
    Get a user by their ID.

    Args:
        user_id: The user's UUID
        session: Database session

    Returns:
        The User if found

    Raises:
        HTTPException: If user not found
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
