from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.services.auth_service import login

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login_endpoint(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    access_token = login(db=db, email=payload.email, password=payload.password)
    return TokenResponse(access_token=access_token, token_type="bearer")
