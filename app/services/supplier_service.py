from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.supplier import Supplier
from app.schemas.supplier_schema import SupplierCreate


def list_suppliers(db: Session) -> list[Supplier]:
    return db.query(Supplier).all()


def get_supplier_by_id(db: Session, supplier_id: int) -> Supplier:
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return supplier


def create_supplier(db: Session, payload: SupplierCreate) -> Supplier:
    supplier = Supplier(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        document_number=payload.document_number,
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier
