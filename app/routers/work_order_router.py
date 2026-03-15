from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import require_current_user
from app.database.session import get_db
from app.schemas.work_order_schema import WorkOrderCreate, WorkOrderResponse
from app.services.work_order_service import (
    create_work_order,
    get_work_order_by_id,
    list_work_orders,
)

router = APIRouter(prefix="/work-orders", tags=["Work Orders"])


@router.get("", response_model=list[WorkOrderResponse])
def list_work_orders_endpoint(db: Session = Depends(get_db)) -> list[WorkOrderResponse]:
    return list_work_orders(db)


@router.get("/{work_order_id}", response_model=WorkOrderResponse)
def get_work_order_endpoint(work_order_id: int, db: Session = Depends(get_db)) -> WorkOrderResponse:
    return get_work_order_by_id(db, work_order_id)


@router.post("", response_model=WorkOrderResponse, status_code=status.HTTP_201_CREATED)
def create_work_order_endpoint(
    payload: WorkOrderCreate,
    _: object = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> WorkOrderResponse:
    return create_work_order(db, payload)
