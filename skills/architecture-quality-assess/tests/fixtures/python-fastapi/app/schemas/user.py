"""User data schemas."""

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""

    name: str
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str


class User(UserBase):
    """User schema with ID."""

    id: int

    class Config:
        """Pydantic configuration."""

        from_attributes = True
