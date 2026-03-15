import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_returns_access_token(test_client, admin_user):
    response = await test_client.post(
        "/auth/login",
        json={"email": admin_user.email, "password": "Admin@123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ticket_creation_requires_authentication(test_client, customer):
    response = await test_client.post(
        "/tickets",
        json={
            "title": "Internet outage",
            "description": "The branch is offline.",
            "priority": "HIGH",
            "customer_id": customer.id,
        },
    )

    assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ticket_creation_persists_record(
    test_client, auth_headers, customer, test_db_session
):
    from app.models.ticket import Ticket

    response = await test_client.post(
        "/tickets",
        headers=auth_headers,
        json={
            "title": "Internet outage",
            "description": "The branch is offline.",
            "priority": "HIGH",
            "customer_id": customer.id,
        },
    )

    assert response.status_code == 201
    ticket_id = response.json()["id"]

    ticket = test_db_session.query(Ticket).filter(Ticket.id == ticket_id).one()
    assert ticket.customer_id == customer.id
    assert ticket.priority == "HIGH"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_work_order_creation_requires_authentication(test_client):
    response = await test_client.post(
        "/work-orders",
        json={
            "ticket_id": 999,
            "assigned_user_id": 999,
            "status": "CREATED",
            "started_at": None,
            "finished_at": None,
        },
    )

    assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.asyncio
async def test_work_order_creation_persists_record(
    test_client, auth_headers, admin_user, customer, test_db_session
):
    from app.models.work_order import WorkOrder

    ticket_response = await test_client.post(
        "/tickets",
        headers=auth_headers,
        json={
            "title": "Dispatch field team",
            "description": "Replace optical transceiver.",
            "priority": "MEDIUM",
            "customer_id": customer.id,
        },
    )
    ticket_id = ticket_response.json()["id"]

    response = await test_client.post(
        "/work-orders",
        headers=auth_headers,
        json={
            "ticket_id": ticket_id,
            "assigned_user_id": admin_user.id,
            "status": "CREATED",
            "started_at": None,
            "finished_at": None,
        },
    )

    assert response.status_code == 201
    work_order_id = response.json()["id"]

    work_order = test_db_session.query(WorkOrder).filter(WorkOrder.id == work_order_id).one()
    assert work_order.ticket_id == ticket_id
    assert work_order.assigned_user_id == admin_user.id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_wallet_transaction_updates_balance(
    test_client, auth_headers, admin_user, test_db_session
):
    wallet_response = await test_client.post(
        "/wallets",
        headers=auth_headers,
        json={"user_id": admin_user.id},
    )
    assert wallet_response.status_code == 201
    wallet_id = wallet_response.json()["id"]

    transaction_response = await test_client.post(
        "/wallets/transactions",
        headers=auth_headers,
        json={
            "wallet_id": wallet_id,
            "type": "DEPOSIT",
            "amount": 1250.5,
            "description": "Escrow funding",
        },
    )

    assert transaction_response.status_code == 201

    balance_response = await test_client.get(f"/wallets/{wallet_id}/balance")
    assert balance_response.status_code == 200
    assert balance_response.json()["balance"] == 1250.5

    transaction_id = transaction_response.json()["id"]
    from app.models.transaction import FinancialTransaction

    transaction = (
        test_db_session.query(FinancialTransaction)
        .filter(FinancialTransaction.id == transaction_id)
        .one()
    )
    assert float(transaction.amount) == 1250.5


@pytest.mark.integration
@pytest.mark.asyncio
async def test_wallet_transaction_requires_authentication(test_client, wallet):
    response = await test_client.post(
        "/wallets/transactions",
        json={
            "wallet_id": wallet.id,
            "type": "DEPOSIT",
            "amount": 10,
            "description": "Unauthorized deposit",
        },
    )

    assert response.status_code == 401
