from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.events.event_publisher import publish_event
from app.events.event_types import EventType
from app.models.role import Role
from app.models.user import User
from app.schemas.user_schema import UserCreate


def create_user(db: Session, payload: UserCreate) -> User:
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    role = db.query(Role).filter(Role.name == payload.role_name.upper()).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role",
        )

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role_id=role.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    publish_event(
        event_type=EventType.USER_CREATED,
        payload={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role_id": user.role_id,
        },
        db=db,
    )

    return user
