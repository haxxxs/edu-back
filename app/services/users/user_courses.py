from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from typing import Optional
import asyncio
from datetime import datetime

from app.models.user import User
from app.models.course import Course
from app.models.user_course import UserCourse, Certificate, CourseStatus
from app.schemas.user_course import (
    UserCoursesResponse, 
    UserCourseResponse, 
    UserCoursesStats, 
    CourseFilterStatus
)

# Простое кэширование в памяти
cache = {}

async def clear_cache_after(key: str, seconds: int):
    """Очистить запись в кэше через указанное количество секунд"""
    await asyncio.sleep(seconds)
    if key in cache:
        del cache[key]

async def get_user_courses_service(
    user_id: int,
    current_user: User,
    limit: int = 10,
    offset: int = 0,
    status: Optional[CourseFilterStatus] = None,
    response: Optional[Response] = None
) -> UserCoursesResponse:
    """
    Сервис для получения курсов пользователя
    
    Аргументы:
        user_id: ID пользователя
        current_user: Текущий пользователь (из JWT токена)
        limit: Максимальное количество курсов
        offset: Смещение для пагинации
        status: Фильтр по статусу курса
        response: Объект ответа FastAPI для установки заголовков кэша
    
    Возвращает:
        UserCoursesResponse: Ответ API с курсами пользователя
    """
    # Проверяем права доступа
    if current_user.id != user_id and not getattr(current_user, 'is_admin', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к курсам другого пользователя"
        )
    
    # Проверяем, существует ли пользователь
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )
    
    # Создаем ключ кэша
    cache_key = f"user_courses:{user_id}:{limit}:{offset}:{status}"
    
    # Проверяем кэш
    if response and cache_key in cache:
        response.headers["X-Cache"] = "HIT"
        return cache[cache_key]
    
    if response:
        response.headers["X-Cache"] = "MISS"
    
    # Строим запрос
    query = UserCourse.filter(user_id=user_id)
    
    # Применяем фильтр статуса
    if status and status != CourseFilterStatus.ALL:
        query = query.filter(status=status.value)
    
    # Получаем общее количество до применения лимита и смещения
    total_count = await query.count()
    
    # Получаем курсы пользователя с данными о курсе
    user_courses = await query.prefetch_related('course').limit(limit).offset(offset).order_by(
        # Сортировка: сначала in_progress, затем по дате последнего доступа по убыванию
        "-status", "-last_accessed_at"
    )
    
    # Формируем данные для ответа
    courses_data = []
    
    for user_course in user_courses:
        # У нас уже есть данные о курсе благодаря prefetch_related
        course = user_course.course
        
        # Проверяем, есть ли сертификат
        has_certificate = user_course.certificate_id is not None
        
        # Формируем данные о курсе
        course_data = UserCourseResponse(
            id=course.id,
            title=course.title,
            coverImage=course.cover_image or course.image_url or "",
            status=user_course.status,
            hasCertificate=has_certificate,
            progress=user_course.progress,
            lastAccessedAt=user_course.last_accessed_at
        )
        
        courses_data.append(course_data)
    
    # Получаем статистику пользователя
    completed_courses = await UserCourse.filter(user_id=user_id, status=CourseStatus.COMPLETED).count()
    active_courses = await UserCourse.filter(user_id=user_id, status=CourseStatus.IN_PROGRESS).count()
    certificates = await Certificate.filter(user_course__user_id=user_id).count()
    
    user_stats = UserCoursesStats(
        completedCourses=completed_courses,
        activeCourses=active_courses,
        certificates=certificates
    )
    
    # Формируем итоговый ответ
    response_data = UserCoursesResponse(
        courses=courses_data,
        totalCount=total_count,
        userStats=user_stats
    )
    
    # Кэшируем результат на 5 минут
    if response:
        cache[cache_key] = response_data
        asyncio.create_task(clear_cache_after(cache_key, 300))  # 5 минут TTL
    
    return response_data 