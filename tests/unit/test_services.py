import pytest


@pytest.mark.unit
def test_create_ticket_service_persists_event_and_tasks(test_db_session, customer):
    from app.models.background_task import BackgroundTask
    from app.models.event_log import EventLog
    from app.schemas.ticket_schema import TicketCreate
    from app.services.ticket_service import create_ticket

    ticket = create_ticket(
        db=test_db_session,
        payload=TicketCreate(
            title="Core link down",
            description="The primary MPLS link is unavailable.",
            customer_id=customer.id,
            priority="HIGH",
        ),
    )

    assert ticket.id is not None

    logged_event = (
        test_db_session.query(EventLog).filter(EventLog.event_type == "TICKET_CREATED").one()
    )
    assert logged_event.payload["id"] == ticket.id

    task_types = {task.task_type for task in test_db_session.query(BackgroundTask).all()}
    assert task_types == {"evaluate_agents", "process_event"}


@pytest.mark.unit
def test_wallet_balance_aggregates_transactions(test_db_session, wallet):
    from app.models.transaction import TransactionType
    from app.schemas.transaction_schema import TransactionCreate
    from app.services.wallet_service import create_transaction, get_wallet_balance

    create_transaction(
        db=test_db_session,
        payload=TransactionCreate(
            wallet_id=wallet.id,
            type=TransactionType.DEPOSIT,
            amount=250.0,
            description="Initial credit",
        ),
    )
    create_transaction(
        db=test_db_session,
        payload=TransactionCreate(
            wallet_id=wallet.id,
            type=TransactionType.PAYMENT,
            amount=50.0,
            description="Invoice payment",
        ),
    )

    assert get_wallet_balance(test_db_session, wallet.id) == 300.0
