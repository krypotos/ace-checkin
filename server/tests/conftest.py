"""
Pytest fixtures for testing the Ace Check-in API.

This module provides fixtures for both unit and integration tests:
- Unit tests: Use mocked dependencies, no database
- Integration tests: Use a real test database
"""

from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_session
from app.main import app
from app.models import EntryLog, Member, PaymentLog, SQLModel

# ==================== Test Database Configuration ====================

# Use SQLite for testing (in-memory for speed)
TEST_DATABASE_URL = "sqlite://"


@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine (SQLite in-memory)."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def test_session(test_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(test_session: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client with database session override.

    This fixture overrides the database dependency to use the test database.
    """

    def override_get_session():
        try:
            yield test_session
        finally:
            pass

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ==================== Sample Data Fixtures ====================


@pytest.fixture
def sample_member(test_session: Session) -> Member:
    """Create a sample member in the test database."""
    member = Member(
        name="Test User",
        email="test@example.com",
        phone="+1-555-0100",
    )
    test_session.add(member)
    test_session.commit()
    test_session.refresh(member)
    return member


@pytest.fixture
def sample_members(test_session: Session) -> list[Member]:
    """Create multiple sample members in the test database."""
    members = [
        Member(name="Alice Johnson", email="alice@example.com", phone="+1-555-0101"),
        Member(name="Bob Smith", email="bob@example.com", phone="+1-555-0102"),
        Member(name="Charlie Brown", email="charlie@example.com", phone="+1-555-0103"),
    ]
    for member in members:
        test_session.add(member)
    test_session.commit()
    for member in members:
        test_session.refresh(member)
    return members


@pytest.fixture
def sample_entry(test_session: Session, sample_member: Member) -> EntryLog:
    """Create a sample entry log in the test database."""
    entry = EntryLog(
        member_id=sample_member.id,
        notes="Test entry",
    )
    test_session.add(entry)
    test_session.commit()
    test_session.refresh(entry)
    return entry


@pytest.fixture
def sample_payment(test_session: Session, sample_member: Member) -> PaymentLog:
    """Create a sample payment log in the test database."""
    payment = PaymentLog(
        member_id=sample_member.id,
        amount=Decimal("25.50"),
        notes="Test payment",
    )
    test_session.add(payment)
    test_session.commit()
    test_session.refresh(payment)
    return payment


# ==================== Request Data Fixtures ====================


@pytest.fixture
def valid_member_data() -> dict:
    """Valid member creation data."""
    return {
        "name": "New Member",
        "email": "new@example.com",
        "phone": "+1-555-9999",
    }


@pytest.fixture
def valid_entry_data(sample_member: Member) -> dict:
    """Valid entry creation data."""
    return {
        "member_id": sample_member.id,
        "notes": "Court A",
    }


@pytest.fixture
def valid_payment_data(sample_member: Member) -> dict:
    """Valid payment creation data."""
    return {
        "member_id": sample_member.id,
        "amount": 50.00,
        "notes": "Monthly fee",
    }
