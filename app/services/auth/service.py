from typing import Optional
from tortoise.exceptions import DoesNotExist, IntegrityError

from app.models.user import User
from app.schemas.auth import UserRegistrationInput
from app.core.security import get_password_hash, verify_password
from app.core.telegram import validate_telegram_id

async def get_user_by_email(email: str) -> Optional[User]:
    """Fetch a user by their email address."""
    try:
        return await User.get(email=email)
    except DoesNotExist:
        return None

async def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate a user based on email and password."""
    user = await get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    # Optional: Check if user is active here as well
    # if not user.is_active:
    #     return None
    return user

async def create_user(user_data: UserRegistrationInput) -> User:
    """
    Create a new user in the database.
    Raises IntegrityError if email already exists.
    """
    # Validate telegram_id
    is_valid, error_message = validate_telegram_id(user_data.telegram_id)
    if not is_valid:
        raise ValueError(f"Invalid Telegram ID: {error_message}")
    
    hashed_pass = get_password_hash(user_data.password)
    
    try:
        user = await User.create(
            email=user_data.email,
            hashed_password=hashed_pass,
            name=user_data.name,
            telegram_id=user_data.telegram_id
        )
        return user
    except IntegrityError as e:
        # Check if it's a telegram_id uniqueness constraint error
        if "telegram_id" in str(e):
            raise IntegrityError("Telegram ID already registered")
        # Handle potential race conditions or re-raise specific errors
        print(f"IntegrityError during user creation: {e}")
        # Re-raise to be caught by the router for a 409 Conflict
        raise IntegrityError("Email already registered")

# Potentially add functions for updating profile, etc. 