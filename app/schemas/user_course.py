from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Literal
from enum import Enum

class CourseFilterStatus(str, Enum):
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    ALL = "all"

class UserCourseResponse(BaseModel):
    """Схема для ответа с курсом пользователя"""
    id: int
    title: str
    coverImage: str
    status: Literal["completed", "in_progress"]
    hasCertificate: bool
    progress: int  # 0-100
    lastAccessedAt: datetime

    class Config:
        orm_mode = True

class UserCoursesStats(BaseModel):
    """Схема для статистики курсов пользователя"""
    completedCourses: int
    activeCourses: int
    certificates: int

class UserCoursesResponse(BaseModel):
    """Схема для ответа API курсов пользователя"""
    courses: List[UserCourseResponse]
    totalCount: int
    userStats: UserCoursesStats

# Параметры запроса
class UserCoursesParams(BaseModel):
    limit: Optional[int] = Field(10, ge=1, le=100, description="Максимальное количество курсов для возврата")
    offset: Optional[int] = Field(0, ge=0, description="Смещение для пагинации")
    status: Optional[CourseFilterStatus] = Field(None, description="Фильтр по статусу курса") 