"""Pydantic schemas for API requests and responses"""
from datetime import datetime
from decimal import Decimal, InvalidOperation

from pydantic import BaseModel, Field, field_validator

# ==================== Member Schemas ====================


class MemberBase(BaseModel):
    """Base member schema"""

    name: str = Field(..., min_length=1, max_length=255)
    email: str | None = None
    phone: str | None = None


class MemberCreate(MemberBase):
    """Schema for creating a member"""

    pass


class MemberResponse(MemberBase):
    """Schema for member response"""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Entry Schemas ====================


class EntryCheckIn(BaseModel):
    """Schema for entry check-in request from mobile app"""

    member_id: int = Field(..., gt=0, description="Member ID from scanned barcode")
    notes: str | None = Field(
        None, max_length=255, description="Optional notes (e.g., court number)"
    )


class EntryResponse(BaseModel):
    """
    Schema for entry response - includes member details for mobile app confirmation
    """

    id: int
    member_id: int
    member_name: str
    timestamp: datetime
    notes: str | None = None
    message: str  # Human-readable confirmation message

    class Config:
        from_attributes = True


# ==================== Payment Schemas ====================


class PaymentCheckIn(BaseModel):
    """Schema for payment request from mobile app"""

    member_id: int = Field(..., gt=0, description="Member ID from scanned barcode")
    amount: Decimal = Field(
        ...,
        gt=0,
        le=1000,
        description="Payment amount in dollars (0.01 to 1000.00, max 2 decimal places)",
    )
    notes: str | None = Field(None, max_length=255, description="Optional payment notes")

    @field_validator("amount")
    @classmethod
    def validate_decimal_places(cls, v: Decimal) -> Decimal:
        """Ensure amount has at most 2 decimal places"""
        try:
            # Convert to Decimal if not already
            decimal_value = Decimal(str(v))
            # Check decimal places by quantizing
            quantized = decimal_value.quantize(Decimal("0.01"))
            if decimal_value != quantized:
                raise ValueError("Amount must have at most 2 decimal places")
            return quantized
        except InvalidOperation as e:
            raise ValueError(f"Invalid decimal value: {e}") from e


class PaymentResponse(BaseModel):
    """
    Schema for payment response - includes member details for mobile app confirmation
    """

    id: int
    member_id: int
    member_name: str
    amount: Decimal  # Amount in dollars
    timestamp: datetime
    notes: str | None = None
    message: str  # Human-readable confirmation message

    class Config:
        from_attributes = True


# ==================== Error Schemas ====================


class ErrorResponse(BaseModel):
    """Schema for error responses"""

    detail: str
    error_code: str | None = None
