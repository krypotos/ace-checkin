"""SQLModel database models"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric
from sqlmodel import Column, DateTime, Field, Integer, SQLModel, String


class Member(SQLModel, table=True):
    """Member model - stores member information"""

    __tablename__ = "members"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(255), nullable=False))
    email: str | None = Field(default=None, sa_column=Column(String(255)))
    phone: str | None = Field(default=None, sa_column=Column(String(20)))
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False, default=datetime.utcnow),
    )


class EntryLog(SQLModel, table=True):
    """Entry log model - tracks when members enter the court"""

    __tablename__ = "entry_logs"

    id: int | None = Field(default=None, primary_key=True)
    member_id: int = Field(sa_column=Column(Integer, nullable=False, index=True))
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False, default=datetime.utcnow),
    )
    notes: str | None = Field(default=None, sa_column=Column(String(255)))


class PaymentLog(SQLModel, table=True):
    """Payment log model - tracks member payments"""

    __tablename__ = "payment_logs"

    id: int | None = Field(default=None, primary_key=True)
    member_id: int = Field(sa_column=Column(Integer, nullable=False, index=True))
    # Amount in dollars, stored as DECIMAL(10,2) for precise monetary values
    # Constraints: > 0 and <= 1000, validated at API level
    amount: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False, default=datetime.utcnow),
    )
    notes: str | None = Field(default=None, sa_column=Column(String(255)))
