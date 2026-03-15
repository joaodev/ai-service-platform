import pytest
from sqlalchemy import inspect, text


@pytest.mark.integration
def test_database_connection_uses_ephemeral_container(test_engine):
    with test_engine.connect() as connection:
        database_name = connection.execute(text("select current_database()")).scalar_one()

    assert database_name == "test_db"


@pytest.mark.integration
def test_expected_tables_exist_after_migrations(test_engine):
    inspector = inspect(test_engine)
    tables = set(inspector.get_table_names())

    assert "users" in tables
    assert "tickets" in tables
    assert "knowledge_documents" in tables
    assert "ai_agent_actions" in tables
