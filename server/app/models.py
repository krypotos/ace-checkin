"""SQLModel database models"""
from datetime import datetime

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
    amount: float = Field(sa_column=Column(Integer, nullable=False))  # in cents
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False, default=datetime.utcnow),
    )
    notes: str | None = Field(default=None, sa_column=Column(String(255)))
