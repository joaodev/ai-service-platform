from typing import Any

from fastapi import HTTPException, status
from langchain.tools import tool
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.rag_service import answer_question
from app.models.user import User
from app.schemas.customer_schema import CustomerCreate
from app.schemas.ticket_schema import TicketCreate
from app.schemas.work_order_schema import WorkOrderCreate
from app.services.customer_service import create_customer
from app.services.ticket_service import create_ticket, list_tickets
from app.services.wallet_service import get_wallet_balance, list_transactions
from app.services.work_order_service import create_work_order


class CreateTicketInput(BaseModel):
    title: str
    description: str | None = None
    customer_id: int
    priority: str = "MEDIUM"


class ListTicketsInput(BaseModel):
    pass


class CreateWorkOrderInput(BaseModel):
    ticket_id: int
    assigned_user_id: int


class GetWalletBalanceInput(BaseModel):
    wallet_id: int


class ListTransactionsInput(BaseModel):
    pass


class CreateCustomerInput(BaseModel):
    name: str
    email: str
    phone: str | None = None
    document_number: str


class QueryKnowledgeInput(BaseModel):
    question: str


def _ensure_not_client(user: User) -> None:
    if user.role and user.role.name == "CLIENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for this action",
        )


def get_agent_tools(db: Session, user: User) -> list[Any]:
    @tool("create_ticket", args_schema=CreateTicketInput)
    def create_ticket_tool(
        title: str, description: str | None, customer_id: int, priority: str
    ) -> dict:
        ticket = create_ticket(
            db=db,
            payload=TicketCreate(
                title=title,
                description=description,
                customer_id=customer_id,
                priority=priority,
            ),
        )
        return {
            "status": "success",
            "ticket": {
                "id": ticket.id,
                "title": ticket.title,
                "status": ticket.status.value,
                "customer_id": ticket.customer_id,
            },
        }

    @tool("list_tickets", args_schema=ListTicketsInput)
    def list_tickets_tool() -> dict:
        tickets = list_tickets(db=db)
        return {
            "count": len(tickets),
            "tickets": [
                {
                    "id": ticket.id,
                    "title": ticket.title,
                    "status": ticket.status.value,
                    "customer_id": ticket.customer_id,
                }
                for ticket in tickets
            ],
        }

    @tool("create_work_order", args_schema=CreateWorkOrderInput)
    def create_work_order_tool(ticket_id: int, assigned_user_id: int) -> dict:
        _ensure_not_client(user)
        work_order = create_work_order(
            db=db,
            payload=WorkOrderCreate(ticket_id=ticket_id, assigned_user_id=assigned_user_id),
        )
        return {
            "status": "success",
            "work_order": {
                "id": work_order.id,
                "ticket_id": work_order.ticket_id,
                "assigned_user_id": work_order.assigned_user_id,
                "status": work_order.status.value,
            },
        }

    @tool("get_wallet_balance", args_schema=GetWalletBalanceInput)
    def get_wallet_balance_tool(wallet_id: int) -> dict:
        balance = get_wallet_balance(db=db, wallet_id=wallet_id)
        return {"wallet_id": wallet_id, "balance": balance}

    @tool("list_transactions", args_schema=ListTransactionsInput)
    def list_transactions_tool() -> dict:
        _ensure_not_client(user)
        transactions = list_transactions(db=db)
        return {
            "count": len(transactions),
            "transactions": [
                {
                    "id": transaction.id,
                    "wallet_id": transaction.wallet_id,
                    "type": transaction.type.value,
                    "amount": float(transaction.amount),
                }
                for transaction in transactions
            ],
        }

    @tool("create_customer", args_schema=CreateCustomerInput)
    def create_customer_tool(
        name: str, email: str, phone: str | None, document_number: str
    ) -> dict:
        _ensure_not_client(user)
        customer = create_customer(
            db=db,
            payload=CustomerCreate(
                name=name,
                email=email,
                phone=phone,
                document_number=document_number,
            ),
        )
        return {
            "status": "success",
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
            },
        }

    @tool("query_knowledge", args_schema=QueryKnowledgeInput)
    def query_knowledge_tool(question: str) -> dict:
        return answer_question(question)

    return [
        create_ticket_tool,
        list_tickets_tool,
        create_work_order_tool,
        get_wallet_balance_tool,
        list_transactions_tool,
        create_customer_tool,
        query_knowledge_tool,
    ]
