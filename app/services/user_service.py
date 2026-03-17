from fastapi import HTTPException, status

from app.models.schemas.user import UserCreate, UserRead
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def create_user(self, payload: UserCreate) -> UserRead:
        existing = self.repository.get_by_email(str(payload.email))
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists.",
            )

        user = self.repository.create(full_name=payload.full_name, email=str(payload.email))
        return UserRead.model_validate(user)

    def get_user(self, user_id: int) -> UserRead:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return UserRead.model_validate(user)

    def list_users(self) -> list[UserRead]:
        return [UserRead.model_validate(user) for user in self.repository.list_all()]
