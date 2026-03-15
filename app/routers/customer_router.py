from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.customer_schema import CustomerCreate, CustomerResponse
from app.services.customer_service import create_customer, get_customer_by_id, list_customers

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=list[CustomerResponse])
def list_customers_endpoint(db: Session = Depends(get_db)) -> list[CustomerResponse]:
    return list_customers(db)


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer_endpoint(customer_id: int, db: Session = Depends(get_db)) -> CustomerResponse:
    return get_customer_by_id(db, customer_id)


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer_endpoint(
    payload: CustomerCreate, db: Session = Depends(get_db)
) -> CustomerResponse:
    return create_customer(db, payload)
