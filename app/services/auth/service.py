from typing import Optional
from tortoise.exceptions import DoesNotExist, IntegrityError

from app.models.user import User
from app.schemas.auth import UserRegistrationInput
from app.core.security import hash_password, verify_password

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
    hashed_pass = hash_password(user_data.password)
    # Create user instance (name, etc., could be added here or updated later)
    # Use create() which handles saving
    try:
        user = await User.create(
            email=user_data.email,
            hashed_password=hashed_pass,
            # Add default name or leave null if allowed
            # name=user_data.email.split('@')[0] # Example default name
        )
        return user
    except IntegrityError as e:
        # Handle potential race conditions or re-raise specific errors
        print(f"IntegrityError during user creation: {e}")
        # Re-raise to be caught by the router for a 409 Conflict
        raise IntegrityError("Email already registered", e)

# Potentially add functions for updating profile, etc. 