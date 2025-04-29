from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from app.core.security import get_admin_user
from app.models.user import User
from app.models.course import Course
from app.models.user_course import UserCourse, Certificate

router = APIRouter()

@router.get("/dashboard", summary="Получение данных для админской панели")
async def admin_dashboard(admin_user: User = Depends(get_admin_user)):
    """
    Получает общую статистику для админской панели
    
    Требует прав администратора
    """
    # Количество пользователей
    total_users = await User.all().count()
    # Количество курсов
    total_courses = await Course.all().count()
    # Количество записей на курсы
    total_enrollments = await UserCourse.all().count()
    # Количество выданных сертификатов
    total_certificates = await Certificate.all().count()
    
    return {
        "statistics": {
            "totalUsers": total_users,
            "totalCourses": total_courses,
            "totalEnrollments": total_enrollments,
            "totalCertificates": total_certificates
        },
        "admin": {
            "id": admin_user.id,
            "name": admin_user.name,
            "email": admin_user.email
        }
    }

@router.get("/users", summary="Получение списка всех пользователей")
async def get_all_users(
    admin_user: User = Depends(get_admin_user),
    limit: Optional[int] = 100,
    offset: Optional[int] = 0
):
    """
    Получает список всех пользователей с пагинацией
    
    Требует прав администратора
    
    - **limit**: Максимальное количество пользователей (по умолчанию: 100)
    - **offset**: Смещение для пагинации
    """
    total = await User.all().count()
    users = await User.all().offset(offset).limit(limit)
    
    return {
        "total": total,
        "users": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "is_admin": user.is_admin,
                "is_active": user.is_active,
                "created_at": user.created_at
            }
            for user in users
        ]
    }

@router.get("/courses", summary="Получение списка всех курсов")
async def get_all_courses(
    admin_user: User = Depends(get_admin_user),
    limit: Optional[int] = 100,
    offset: Optional[int] = 0
):
    """
    Получает список всех курсов с пагинацией
    
    Требует прав администратора
    
    - **limit**: Максимальное количество курсов (по умолчанию: 100)
    - **offset**: Смещение для пагинации
    """
    total = await Course.all().count()
    courses = await Course.all().offset(offset).limit(limit)
    
    return {
        "total": total,
        "courses": [
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "is_active": course.is_active,
                "created_at": course.created_at
            }
            for course in courses
        ]
    }

@router.get("/user-courses", summary="Получение всех записей пользователей на курсы")
async def get_all_user_courses(
    admin_user: User = Depends(get_admin_user),
    limit: Optional[int] = 100,
    offset: Optional[int] = 0
):
    """
    Получает список всех записей пользователей на курсы с пагинацией
    
    Требует прав администратора
    
    - **limit**: Максимальное количество записей (по умолчанию: 100)
    - **offset**: Смещение для пагинации
    """
    total = await UserCourse.all().count()
    user_courses = await UserCourse.all().prefetch_related('user', 'course').offset(offset).limit(limit)
    
    return {
        "total": total,
        "enrollments": [
            {
                "id": uc.id,
                "user_id": uc.user.id,
                "user_name": uc.user.name,
                "course_id": uc.course.id,
                "course_title": uc.course.title,
                "progress": uc.progress,
                "status": uc.status,
                "started_at": uc.started_at,
                "last_accessed_at": uc.last_accessed_at,
                "completed_at": uc.completed_at,
                "has_certificate": uc.certificate_id is not None
            }
            for uc in user_courses
        ]
    }

@router.put("/users/{user_id}/admin", summary="Назначение/снятие прав администратора")
async def toggle_admin_status(
    user_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """
    Назначает или снимает права администратора у пользователя
    
    Требует прав администратора
    
    - **user_id**: ID пользователя
    """
    # Запрещаем снимать права у самого себя
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невозможно изменить права администратора для собственной учетной записи"
        )
    
    # Находим пользователя
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )
    
    # Инвертируем статус админа
    user.is_admin = not user.is_admin
    await user.save()
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_admin": user.is_admin,
        "message": f"Статус администратора {'назначен' if user.is_admin else 'снят'}"
    } 