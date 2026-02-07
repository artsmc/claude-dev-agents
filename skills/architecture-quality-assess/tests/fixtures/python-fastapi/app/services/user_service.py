"""User business logic service."""

from typing import List, Optional
from app.schemas.user import User, UserCreate


class UserService:
    """Service for user-related business logic."""

    def __init__(self):
        """Initialize user service."""
        self.users = [
            User(id=1, name="John Doe", email="john@example.com"),
            User(id=2, name="Jane Smith", email="jane@example.com"),
        ]
        self.next_id = 3

    def get_all_users(self) -> List[User]:
        """Get all users.

        Returns:
            List of all users.
        """
        return self.users

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID.

        Args:
            user_id: User ID to retrieve.

        Returns:
            User if found, None otherwise.
        """
        for user in self.users:
            if user.id == user_id:
                return user
        return None

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user.

        Args:
            user_data: User creation data.

        Returns:
            Created user with ID.
        """
        new_user = User(
            id=self.next_id,
            name=user_data.name,
            email=user_data.email,
        )
        self.users.append(new_user)
        self.next_id += 1
        return new_user
