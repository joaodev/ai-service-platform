import logging

from fastapi import Depends, FastAPI

from app.ai.agent_router import router as agent_router
from app.core.logging_config import setup_logging
from app.core.security import require_current_user
from app.routers.ai_router import router as ai_router
from app.routers.auth_router import router as auth_router
from app.routers.customer_router import router as customer_router
from app.routers.finance_router import router as finance_router
from app.routers.product_router import router as product_router
from app.routers.service_router import router as service_router
from app.routers.supplier_router import router as supplier_router
from app.routers.task_router import router as task_router
from app.routers.ticket_router import router as ticket_router
from app.routers.user_router import router as user_router
from app.routers.wallet_router import router as wallet_router
from app.routers.webhook_router import router as webhook_router
from app.routers.work_order_router import router as work_order_router

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
def root() -> dict[str, str]:
    logger.info("Root endpoint called")
    return {"message": "API running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(user_router, dependencies=[Depends(require_current_user)])
app.include_router(ai_router, dependencies=[Depends(require_current_user)])
app.include_router(agent_router, dependencies=[Depends(require_current_user)])
app.include_router(customer_router, dependencies=[Depends(require_current_user)])
app.include_router(supplier_router, dependencies=[Depends(require_current_user)])
app.include_router(product_router, dependencies=[Depends(require_current_user)])
app.include_router(service_router, dependencies=[Depends(require_current_user)])
app.include_router(ticket_router, dependencies=[Depends(require_current_user)])
app.include_router(work_order_router, dependencies=[Depends(require_current_user)])
app.include_router(wallet_router, dependencies=[Depends(require_current_user)])
app.include_router(finance_router, dependencies=[Depends(require_current_user)])
app.include_router(webhook_router, dependencies=[Depends(require_current_user)])
app.include_router(task_router, dependencies=[Depends(require_current_user)])
