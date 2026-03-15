from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import require_admin_user
from app.database.session import get_db
from app.schemas.user_schema import UserCreate, UserResponse
from app.services.user_service import create_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(
    payload: UserCreate,
    _: object = Depends(require_admin_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    user = create_user(db=db, payload=payload)
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.name,
        created_at=user.created_at,
    )
