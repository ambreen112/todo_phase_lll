"""Authentication API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from src.core.security import password_hasher, jwt_manager
from src.models.database import get_session
from src.models.user import User
from src.models.schemas import SignupRequest, LoginRequest, AuthResponse, ErrorResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        409: {"model": ErrorResponse, "description": "Email already registered"},
    },
)
async def signup(
    request: SignupRequest,
    session: Session = Depends(get_session),
) -> AuthResponse:
    """
    Create a new user account.

    Args:
        request: Signup request with email and password
        session: Database session

    Returns:
        AuthResponse with JWT token

    Raises:
        HTTPException: If email already exists or validation fails
    """
    # Check if email already exists
    existing = session.exec(select(User).where(User.email == request.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Hash password and create user
    hashed_password = password_hasher.hash_password(request.password)
    user = User(email=request.email, password_hash=hashed_password)

    session.add(user)
    session.commit()
    session.refresh(user)

    # Generate JWT token
    access_token = jwt_manager.create_access_token(
        user_id=user.id,
        email=user.email,
    )

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    },
)
async def login(
    request: LoginRequest,
    session: Session = Depends(get_session),
) -> AuthResponse:
    """
    Authenticate user and return JWT token.

    Args:
        request: Login request with email and password
        session: Database session

    Returns:
        AuthResponse with JWT token

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = session.exec(select(User).where(User.email == request.email)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not password_hasher.verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT token
    access_token = jwt_manager.create_access_token(
        user_id=user.id,
        email=user.email,
    )

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
    )
