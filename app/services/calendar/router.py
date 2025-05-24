from fastapi import APIRouter, HTTPException, Query, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from datetime import datetime, timedelta
import logging

from app.models.calendar import CalendarNote
from app.models.user import User
from app.schemas.calendar import CalendarNoteCreate, CalendarNoteResponse, CalendarNoteUpdate
from app.core.security import get_current_active_user
from app.services.telegram_service import telegram_service

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

@router.post("/notes", response_model=CalendarNoteResponse)
async def create_calendar_note(
    note: CalendarNoteCreate,
    current_user: User = Depends(get_current_active_user),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Create a new calendar note and send Telegram notification"""
    try:
        # Создаем заметку в базе данных
        note_obj = await CalendarNote.create(**note.dict())
        
        # Отправляем уведомление в Telegram, если у пользователя есть telegram_id
        if current_user.telegram_id:
            try:
                await telegram_service.send_calendar_notification(
                    telegram_id=current_user.telegram_id,
                    note_title=note.title,
                    note_date=note.date.strftime("%d.%m.%Y %H:%M"),
                    note_description=note.description,
                    notification_type="created"
                )
                logger.info(f"Telegram notification sent to user {current_user.id}")
            except Exception as e:
                # Логируем ошибку, но не прерываем создание заметки
                logger.error(f"Failed to send Telegram notification to user {current_user.id}: {e}")
        else:
            logger.info(f"User {current_user.id} has no Telegram ID, skipping notification")
        
        return CalendarNoteResponse.from_orm(note_obj)
        
    except Exception as e:
        logger.error(f"Error creating calendar note: {e}")
        raise HTTPException(status_code=500, detail="Failed to create calendar note")

@router.put("/notes/{note_id}", response_model=CalendarNoteResponse)
async def update_calendar_note(
    note_id: int,
    note_update: CalendarNoteUpdate,
    current_user: User = Depends(get_current_active_user),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Update a calendar note and send notification"""
    try:
        # Находим заметку
        note = await CalendarNote.get_or_none(id=note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Calendar note not found")
        
        # Обновляем поля заметки
        update_data = note_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(note, field, value)
        
        await note.save()
        
        # Отправляем уведомление об обновлении
        if current_user.telegram_id:
            try:
                await telegram_service.send_calendar_notification(
                    telegram_id=current_user.telegram_id,
                    note_title=note.title,
                    note_date=note.date.strftime("%d.%m.%Y %H:%M"),
                    note_description=note.description,
                    notification_type="updated"
                )
                logger.info(f"Update notification sent to user {current_user.id}")
            except Exception as e:
                logger.error(f"Failed to send update notification to user {current_user.id}: {e}")
        
        return CalendarNoteResponse.from_orm(note)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating calendar note: {e}")
        raise HTTPException(status_code=500, detail="Failed to update calendar note")

@router.get("/notes", response_model=List[CalendarNoteResponse])
async def list_calendar_notes(
    start_date: datetime = Query(..., description="Start date for filtering notes"),
    end_date: datetime = Query(..., description="End date for filtering notes"),
    is_important: bool = Query(None, description="Filter by importance"),
    current_user: User = Depends(get_current_active_user),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """List calendar notes with date range filtering"""
    query = CalendarNote.filter(date__gte=start_date, date__lte=end_date)
    
    if is_important is not None:
        query = query.filter(is_important=is_important)
    
    notes = await query
    return [CalendarNoteResponse.from_orm(note) for note in notes]

@router.get("/notes/today", response_model=List[CalendarNoteResponse])
async def get_today_notes(
    current_user: User = Depends(get_current_active_user),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Get all notes for today"""
    today = datetime.now().date()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
    
    notes = await CalendarNote.filter(
        date__gte=start_of_day,
        date__lte=end_of_day
    ).order_by('date')
    
    return [CalendarNoteResponse.from_orm(note) for note in notes]

@router.get("/notes/upcoming", response_model=List[CalendarNoteResponse])
async def get_upcoming_notes(
    hours: int = Query(24, description="Hours ahead to look for upcoming notes"),
    current_user: User = Depends(get_current_active_user),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Get upcoming notes within specified hours"""
    now = datetime.now()
    future_time = now + timedelta(hours=hours)
    
    notes = await CalendarNote.filter(
        date__gte=now,
        date__lte=future_time
    ).order_by('date')
    
    return [CalendarNoteResponse.from_orm(note) for note in notes]

@router.post("/notes/{note_id}/remind")
async def send_note_reminder(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Send immediate reminder for a specific note"""
    try:
        note = await CalendarNote.get_or_none(id=note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Calendar note not found")
        
        if not current_user.telegram_id:
            raise HTTPException(status_code=400, detail="User has no Telegram ID configured")
        
        # Отправляем напоминание
        success = await telegram_service.send_calendar_notification(
            telegram_id=current_user.telegram_id,
            note_title=note.title,
            note_date=note.date.strftime("%d.%m.%Y %H:%M"),
            note_description=note.description,
            notification_type="reminder"
        )
        
        if success:
            return {"success": True, "message": "Reminder sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send reminder")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending reminder: {e}")
        raise HTTPException(status_code=500, detail="Failed to send reminder")

@router.post("/notifications/daily-reminder")
async def send_daily_reminder(
    current_user: User = Depends(get_current_active_user),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Send daily reminder with today's notes"""
    try:
        if not current_user.telegram_id:
            raise HTTPException(status_code=400, detail="User has no Telegram ID configured")
        
        # Получаем заметки на сегодня
        today = datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        
        notes = await CalendarNote.filter(
            date__gte=start_of_day,
            date__lte=end_of_day
        ).order_by('date')
        
        # Формируем список заметок для уведомления
        upcoming_notes = []
        for note in notes:
            upcoming_notes.append({
                'title': note.title,
                'time': note.date.strftime("%H:%M"),
                'description': note.description
            })
        
        # Отправляем ежедневное напоминание
        success = await telegram_service.send_daily_reminder(
            telegram_id=current_user.telegram_id,
            notes_count=len(notes),
            upcoming_notes=upcoming_notes
        )
        
        if success:
            return {
                "success": True, 
                "message": "Daily reminder sent successfully",
                "notes_count": len(notes)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send daily reminder")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending daily reminder: {e}")
        raise HTTPException(status_code=500, detail="Failed to send daily reminder")

@router.get("/notes/{note_id}", response_model=CalendarNoteResponse)
async def get_calendar_note(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Get a specific calendar note by ID"""
    note = await CalendarNote.get_or_none(id=note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Calendar note not found")
    return CalendarNoteResponse.from_orm(note)

@router.delete("/notes/{note_id}", response_model=dict)
async def delete_calendar_note(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Delete a calendar note and send notification"""
    try:
        note = await CalendarNote.get_or_none(id=note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Calendar note not found")
        
        # Сохраняем данные заметки для уведомления
        note_title = note.title
        note_date = note.date.strftime("%d.%m.%Y %H:%M")
        note_description = note.description
        
        # Удаляем заметку
        await note.delete()
        
        # Отправляем уведомление об удалении
        if current_user.telegram_id:
            try:
                await telegram_service.send_calendar_notification(
                    telegram_id=current_user.telegram_id,
                    note_title=note_title,
                    note_date=note_date,
                    note_description=note_description,
                    notification_type="deleted"
                )
                logger.info(f"Delete notification sent to user {current_user.id}")
            except Exception as e:
                logger.error(f"Failed to send delete notification to user {current_user.id}: {e}")
        
        return {"success": True, "message": "Calendar note deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting calendar note: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete calendar note") 