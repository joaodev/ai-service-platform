from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.product_schema import ProductCreate, ProductResponse
from app.services.product_service import create_product, get_product_by_id, list_products

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[ProductResponse])
def list_products_endpoint(db: Session = Depends(get_db)) -> list[ProductResponse]:
    return list_products(db)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_endpoint(product_id: int, db: Session = Depends(get_db)) -> ProductResponse:
    return get_product_by_id(db, product_id)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(
    payload: ProductCreate, db: Session = Depends(get_db)
) -> ProductResponse:
    return create_product(db, payload)
