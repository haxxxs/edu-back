from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

@router.get("/")
async def list_users():
    """Placeholder for listing users"""
    return {"message": "Users list not implemented yet"}

@router.post("/")
async def create_user():
    """Placeholder for creating a user"""
    return {"message": "User creation not implemented yet"}
