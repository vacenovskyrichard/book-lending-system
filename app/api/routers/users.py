from fastapi import APIRouter, Depends, status

from app.dependencies import get_user_service
from app.models.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    return service.create_user(payload)


@router.get("", response_model=list[UserRead])
def list_users(service: UserService = Depends(get_user_service)) -> list[UserRead]:
    return service.list_users()


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    return service.get_user(user_id)
