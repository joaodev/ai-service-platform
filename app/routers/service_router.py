from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.service_schema import ServiceCreate, ServiceResponse
from app.services.service_service import create_service, get_service_by_id, list_services

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("", response_model=list[ServiceResponse])
def list_services_endpoint(db: Session = Depends(get_db)) -> list[ServiceResponse]:
    return list_services(db)


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service_endpoint(service_id: int, db: Session = Depends(get_db)) -> ServiceResponse:
    return get_service_by_id(db, service_id)


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service_endpoint(
    payload: ServiceCreate, db: Session = Depends(get_db)
) -> ServiceResponse:
    return create_service(db, payload)
