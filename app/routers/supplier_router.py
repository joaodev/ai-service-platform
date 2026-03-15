from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.supplier_schema import SupplierCreate, SupplierResponse
from app.services.supplier_service import create_supplier, get_supplier_by_id, list_suppliers

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("", response_model=list[SupplierResponse])
def list_suppliers_endpoint(db: Session = Depends(get_db)) -> list[SupplierResponse]:
    return list_suppliers(db)


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier_endpoint(supplier_id: int, db: Session = Depends(get_db)) -> SupplierResponse:
    return get_supplier_by_id(db, supplier_id)


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier_endpoint(
    payload: SupplierCreate, db: Session = Depends(get_db)
) -> SupplierResponse:
    return create_supplier(db, payload)
