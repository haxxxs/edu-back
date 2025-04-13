from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import datetime

from app.models.calendar import CalendarNote
from app.schemas.calendar import CalendarNoteCreate, CalendarNoteResponse

router = APIRouter()

@router.post("/notes", response_model=CalendarNoteResponse)
async def create_calendar_note(note: CalendarNoteCreate):
    """Create a new calendar note"""
    note_obj = await CalendarNote.create(**note.dict())
    return CalendarNoteResponse.from_orm(note_obj)

@router.get("/notes", response_model=List[CalendarNoteResponse])
async def list_calendar_notes(
    start_date: datetime = Query(..., description="Start date for filtering notes"),
    end_date: datetime = Query(..., description="End date for filtering notes"),
    is_important: bool = Query(None, description="Filter by importance")
):
    """List calendar notes with date range filtering"""
    query = CalendarNote.filter(date__gte=start_date, date__lte=end_date)
    
    if is_important is not None:
        query = query.filter(is_important=is_important)
    
    notes = await query
    return [CalendarNoteResponse.from_orm(note) for note in notes]

@router.get("/notes/{note_id}", response_model=CalendarNoteResponse)
async def get_calendar_note(note_id: int):
    """Get a specific calendar note by ID"""
    note = await CalendarNote.get_or_none(id=note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Calendar note not found")
    return CalendarNoteResponse.from_orm(note)

@router.delete("/notes/{note_id}", response_model=dict)
async def delete_calendar_note(note_id: int):
    """Delete a calendar note"""
    note = await CalendarNote.get_or_none(id=note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Calendar note not found")
    
    await note.delete()
    return {"message": "Calendar note deleted successfully"} 