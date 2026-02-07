"""User API routes."""

from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.user import User, UserCreate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])
user_service = UserService()


@router.get("/", response_model=List[User])
async def list_users():
    """List all users."""
    return user_service.get_all_users()


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Get user by ID."""
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=User, status_code=201)
async def create_user(user_data: UserCreate):
    """Create a new user."""
    return user_service.create_user(user_data)
