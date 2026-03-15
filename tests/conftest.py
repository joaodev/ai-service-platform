from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from faker import Faker
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer

PROJECT_ROOT = Path(__file__).resolve().parents[1]
POSTGRES_IMAGE = "pgvector/pgvector:pg15"


def _configure_test_environment(database_url: str) -> None:
    os.environ["DATABASE_URL"] = database_url
    os.environ["JWT_SECRET_KEY"] = "test-secret-key"
    os.environ["AZURE_OPENAI_ENDPOINT"] = ""
    os.environ["AZURE_OPENAI_API_KEY"] = ""
    os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"] = ""
    os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"] = ""


def _run_migrations() -> None:
    alembic_config = Config(str(PROJECT_ROOT / "alembic.ini"))
    alembic_config.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    command.upgrade(alembic_config, "head")


def _truncate_all_tables(engine: Engine) -> None:
    from app.database.base import Base

    with engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE'))


def _get_or_create_role(db: Session, name: str):
    from app.models.role import Role

    role = db.query(Role).filter(Role.name == name).first()
    if role:
        return role

    role = Role(name=name)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    container = PostgresContainer(
        image=POSTGRES_IMAGE,
        dbname="test_db",
        username="test_user",
        password="test_password",
    )
    container.start()
    try:
        _configure_test_environment(container.get_connection_url())
        _run_migrations()
        yield container
    finally:
        container.stop()


@pytest.fixture(scope="session")
def test_engine(postgres_container: PostgresContainer) -> Generator[Engine, None, None]:
    engine = create_engine(os.environ["DATABASE_URL"], future=True)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(scope="session")
def test_session_factory(test_engine: Engine) -> sessionmaker:
    return sessionmaker(bind=test_engine, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True)
def clean_database(test_engine: Engine) -> Generator[None, None, None]:
    _truncate_all_tables(test_engine)
    yield
    _truncate_all_tables(test_engine)


@pytest.fixture(autouse=True)
def stub_async_dispatch(
    monkeypatch: pytest.MonkeyPatch, postgres_container: PostgresContainer
) -> None:
    from app.workers.celery_app import celery_app

    def fake_send_task(*args, **kwargs) -> SimpleNamespace:
        return SimpleNamespace(id=f"test-task-{uuid4()}")

    monkeypatch.setattr(celery_app, "send_task", fake_send_task)


@pytest.fixture
def faker() -> Faker:
    return Faker()


@pytest.fixture
def test_db_session(
    test_session_factory: sessionmaker, postgres_container: PostgresContainer
) -> Generator[Session, None, None]:
    session = test_session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def admin_user(test_db_session: Session):
    from app.core.security import hash_password
    from app.models.user import User

    admin_role = _get_or_create_role(test_db_session, "ADMIN")
    user = User(
        name="Admin Test User",
        email="admin@test.local",
        password_hash=hash_password("Admin@123"),
        role_id=admin_role.id,
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user


@pytest.fixture
def client_user(test_db_session: Session):
    from app.core.security import hash_password
    from app.models.user import User

    client_role = _get_or_create_role(test_db_session, "CLIENT")
    user = User(
        name="Client Test User",
        email="client@test.local",
        password_hash=hash_password("Client@123"),
        role_id=client_role.id,
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user


@pytest.fixture
def customer(test_db_session: Session, faker: Faker):
    from app.models.customer import Customer

    record = Customer(
        name=faker.company(),
        email=faker.unique.email(),
        phone=faker.phone_number(),
        document_number=faker.unique.numerify(text="###########"),
    )
    test_db_session.add(record)
    test_db_session.commit()
    test_db_session.refresh(record)
    return record


@pytest.fixture
def wallet(test_db_session: Session, admin_user):
    from app.models.wallet import Wallet

    record = Wallet(user_id=admin_user.id)
    test_db_session.add(record)
    test_db_session.commit()
    test_db_session.refresh(record)
    return record


@pytest_asyncio.fixture
async def test_client(test_db_session: Session, postgres_container: PostgresContainer):
    from app.database.session import get_db
    from app.main import app

    def override_get_db() -> Generator[Session, None, None]:
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_token(test_client: AsyncClient, admin_user) -> str:
    response = await test_client.post(
        "/auth/login",
        json={"email": admin_user.email, "password": "Admin@123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def auth_headers(auth_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {auth_token}"}
