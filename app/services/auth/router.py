from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # Use for login form data
from tortoise.exceptions import IntegrityError
from datetime import timedelta

from app.models.user import User
from app.schemas.auth import UserRegistrationInput, AuthResponse, MessageResponse
from app.schemas.user import UserProfile, Token
from app.services.auth import service as auth_service
from app.core.security import create_access_token, get_current_active_user, authenticate_user
from app.core.config import settings

router = APIRouter()

@router.post("/register", 
             response_model=MessageResponse, 
             status_code=status.HTTP_201_CREATED,
             summary="Register a new user")
async def register_user(user_in: UserRegistrationInput):
    """Register a new user account."""
    try:
        user = await auth_service.create_user(user_in)
        # Optionally log the user in immediately and return a token,
        # but current spec asks for a message.
        return MessageResponse(message=f"User {user.email} registered successfully. Please login.")
    except ValueError as e:
        # Handle Telegram ID validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except IntegrityError as e:
        if "Telegram ID already registered" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Telegram ID already registered",
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    except Exception as e:
        # Catch other potential errors during creation
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during registration: {e}",
        )

@router.post("/login", response_model=AuthResponse, summary="User login")
async def login_for_access_token(
    # Use OAuth2PasswordRequestForm: expects form data with 'username' and 'password'
    # Frontend needs to send data as form-data, not JSON
    # Alternatively, use UserLoginInput and expect JSON
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Authenticate user and return JWT token with admin status."""
    # Note: OAuth2PasswordRequestForm uses 'username' field for the email
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем, является ли пользователь админом
    # Если это предопределенная учетная запись админа, устанавливаем флаг
    admin_email = "admin@admin.ru"
    admin_password = "ghjhjr11"
    
    if form_data.username == admin_email and form_data.password == admin_password:
        if not user.is_admin:
            user.is_admin = True
            await user.save()
    
    # Создаем токен
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "admin": user.is_admin},
        expires_delta=access_token_expires
    )
    
    # Возвращаем токен, информацию об админе и данные пользователя
    return AuthResponse(
        token=access_token,
        token_type="bearer",
        is_admin=user.is_admin,
        user_id=user.id,
        email=user.email,
        telegram_id=user.telegram_id
    )

# Example using JSON input instead of form data for login
# @router.post("/login/json", response_model=AuthResponse, summary="User login (JSON input)")
# async def login_for_access_token_json(user_in: UserLoginInput):
#     user = await auth_service.authenticate_user(email=user_in.email, password=user_in.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token = create_access_token(data={"sub": user.email})
#     return AuthResponse(token=access_token)

@router.get("/profile", 
            response_model=UserProfile, 
            summary="Get current user profile",
            dependencies=[Depends(get_current_active_user)]) # Ensures user is authenticated and active
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Fetch the profile of the currently authenticated user."""
    # Map ORM model to Pydantic schema, respecting aliases
    profile_data = UserProfile(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role, # Enum should serialize correctly based on schema config
        avatarUrl=current_user.avatar_url, # Map avatar_url to avatarUrl
        about=current_user.about,
        location=current_user.location,
        telegram_id=current_user.telegram_id,
        joinedAt=current_user.created_at # Map created_at to joinedAt
        # stats=... # Fetch and add stats if implemented
    )
    return profile_data 