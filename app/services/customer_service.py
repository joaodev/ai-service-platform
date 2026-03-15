from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer_schema import CustomerCreate


def list_customers(db: Session) -> list[Customer]:
    return db.query(Customer).all()


def get_customer_by_id(db: Session, customer_id: int) -> Customer:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


def create_customer(db: Session, payload: CustomerCreate) -> Customer:
    customer = Customer(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        document_number=payload.document_number,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer
