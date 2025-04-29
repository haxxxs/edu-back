from fastapi import APIRouter, HTTPException, Depends, Query, status, Response
from typing import List, Optional

from app.models.user import User
from app.schemas.user_course import UserCoursesResponse, CourseFilterStatus
from app.services.users.user_courses import get_user_courses_service

# Импортируем функцию для получения текущего пользователя из JWT
from app.core.security import get_current_user

router = APIRouter()

@router.get("/")
async def list_users():
    """Placeholder for listing users"""
    return {"message": "Users list not implemented yet"}

@router.post("/")
async def create_user():
    """Placeholder for creating a user"""
    return {"message": "User creation not implemented yet"}

@router.get("/{user_id}/courses", response_model=UserCoursesResponse)
async def get_user_courses(
    user_id: int,
    response: Response,
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество курсов"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    status: Optional[CourseFilterStatus] = Query(None, description="Фильтр по статусу курса"),
    current_user: User = Depends(get_current_user)
):
    """
    Получить курсы пользователя с возможностью фильтрации и пагинации
    
    - **user_id**: ID пользователя
    - **limit**: Максимальное количество курсов (по умолчанию: 10, макс: 100)
    - **offset**: Смещение для пагинации
    - **status**: Фильтр по статусу курса (completed, in_progress, all)
    
    Требуется авторизация через JWT токен. Пользователь может просматривать только свои курсы, 
    администратор может просматривать курсы любого пользователя.
    """
    return await get_user_courses_service(
        user_id=user_id,
        current_user=current_user,
        limit=limit,
        offset=offset,
        status=status,
        response=response
    )
