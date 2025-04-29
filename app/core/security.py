from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserInDB, TokenData
# Import service later to avoid circular dependency if get_user is moved there
# from app.services.auth.service import get_user_by_email

# --- Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def authenticate_user(username_or_email: str, password: str):
    """Аутентификация пользователя по email/username и паролю"""
    # Поиск пользователя по email или username
    user = await User.get_or_none(email=username_or_email)
    
    # Если пользователь не найден или пароль неверный - возвращаем None
    if not user or not verify_password(password, user.hashed_password):
        return None
    
    return user

# --- JWT Handling ---
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Define the scheme (points to the login endpoint)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Dependency for getting current user ---
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невозможно подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        is_admin: bool = payload.get("admin", False)
        
        if user_id is None:
            raise credentials_exception
        
        token_data = TokenData(user_id=int(user_id), is_admin=is_admin)
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = await User.get_or_none(id=token_data.user_id)
    
    if user is None:
        raise credentials_exception
    # Optional: Check if user is active
    # if not user.is_active:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
        
    # Return the ORM User object
    return user

# Dependency for optional user (e.g., for public profile pages)
async def get_optional_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[User]:
    if token is None:
        return None
    try:
        return await get_current_user(token)
    except HTTPException:
        return None

# Dependency for getting the active user (example)
async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь неактивен")
    return current_user

async def get_admin_user(current_user = Depends(get_current_user)):
    """Проверяет, что пользователь является администратором"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения этой операции"
        )
    return current_user 