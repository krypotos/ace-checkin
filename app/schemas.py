"""Pydantic schemas for API requests and responses"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MemberBase(BaseModel):
    """Base member schema"""
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = None
    phone: Optional[str] = None


class MemberCreate(MemberBase):
    """Schema for creating a member"""
    pass


class MemberResponse(MemberBase):
    """Schema for member response"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class EntryCheckIn(BaseModel):
    """Schema for check-in request"""
    member_id: int = Field(..., gt=0)
    notes: Optional[str] = None


class EntryLogResponse(BaseModel):
    """Schema for entry log response"""
    id: int
    member_id: str
    timestamp: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class PaymentCheckIn(BaseModel):
    """Schema for payment request"""
    member_id: int = Field(..., gt=0)
    amount: float = Field(..., gt=0, description="Amount in dollars")
    notes: Optional[str] = None


class PaymentLogResponse(BaseModel):
    """Schema for payment log response"""
    id: int
    member_id: str
    amount: float
    timestamp: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str
    error_code: Optional[str] = None

