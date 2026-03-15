from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product_schema import ProductCreate


def list_products(db: Session) -> list[Product]:
    return db.query(Product).all()


def get_product_by_id(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def create_product(db: Session, payload: ProductCreate) -> Product:
    product = Product(
        name=payload.name,
        description=payload.description,
        price=payload.price,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
