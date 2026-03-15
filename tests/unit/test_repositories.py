import pytest


@pytest.mark.unit
def test_user_query_by_email_returns_created_user(test_db_session, admin_user):
    from app.models.user import User

    record = test_db_session.query(User).filter(User.email == admin_user.email).one()

    assert record.id == admin_user.id
    assert record.role.name == "ADMIN"


@pytest.mark.unit
def test_ticket_relationship_loads_customer(test_db_session, customer):
    from app.models.ticket import Ticket, TicketStatus

    ticket = Ticket(
        title="Customer edge offline",
        description="Edge router unreachable",
        status=TicketStatus.OPEN,
        priority="MEDIUM",
        customer_id=customer.id,
    )
    test_db_session.add(ticket)
    test_db_session.commit()
    test_db_session.refresh(ticket)

    stored_ticket = test_db_session.query(Ticket).filter(Ticket.id == ticket.id).one()
    assert stored_ticket.customer.email == customer.email
