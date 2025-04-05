from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

@router.get("/")
async def list_tasks():
    """Placeholder for listing tasks"""
    return {"message": "Tasks list not implemented yet"}

@router.post("/")
async def create_task():
    """Placeholder for creating a task"""
    return {"message": "Task creation not implemented yet"}
