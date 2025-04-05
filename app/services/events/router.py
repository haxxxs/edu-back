from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.models.event import Event, EventType
from app.schemas.event import EventCreate, EventResponse

router = APIRouter()

@router.post("/", response_model=EventResponse)
async def create_event(event: EventCreate):
    """Create a new event"""
    event_obj = await Event.create(**event.dict())
    return EventResponse.from_orm(event_obj)

@router.get("/", response_model=List[EventResponse])
async def list_events(
    type: Optional[EventType] = None,
    is_online: Optional[bool] = None,
    min_participants: Optional[int] = Query(None, ge=0),
    max_participants: Optional[int] = Query(None, ge=0)
):
    """List events with optional filtering"""
    query = Event.all()
    
    if type:
        query = query.filter(type=type)
    
    if is_online is not None:
        query = query.filter(is_online=is_online)
    
    if min_participants is not None:
        query = query.filter(current_participants__gte=min_participants)
    
    if max_participants is not None:
        query = query.filter(max_participants__lte=max_participants)
    
    events = await query
    return [EventResponse.from_orm(event) for event in events]

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int):
    """Get a specific event by ID"""
    event = await Event.get_or_none(id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventResponse.from_orm(event)

@router.put("/{event_id}/register", response_model=EventResponse)
async def register_for_event(event_id: int):
    """Register for an event"""
    event = await Event.get_or_none(id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if event.max_participants and event.current_participants >= event.max_participants:
        raise HTTPException(status_code=400, detail="Event is already full")
    
    event.current_participants += 1
    await event.save()
    
    return EventResponse.from_orm(event)

@router.delete("/{event_id}", response_model=dict)
async def delete_event(event_id: int):
    """Delete an event"""
    event = await Event.get_or_none(id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    await event.delete()
    return {"message": "Event deleted successfully"}
