from fastapi import Depends, HTTPException, status
from app.core.security import get_current_user, get_admin_user

async def get_current_admin_user(current_user = Depends(get_current_user)):
    """Проверяет, что пользователь является администратором"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения этой операции"
        )
    return current_user 