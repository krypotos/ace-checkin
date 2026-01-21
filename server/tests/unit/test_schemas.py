"""
Unit tests for Pydantic schemas.

These tests validate request/response schemas without database access.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas import EntryCheckIn, MemberCreate, PaymentCheckIn


class TestMemberCreate:
    """Tests for MemberCreate schema."""

    def test_valid_member_with_all_fields(self):
        """Test creating a member with all fields."""
        member = MemberCreate(
            name="John Doe",
            email="john@example.com",
            phone="+1-555-1234",
        )
        assert member.name == "John Doe"
        assert member.email == "john@example.com"
        assert member.phone == "+1-555-1234"

    def test_valid_member_with_required_only(self):
        """Test creating a member with only required fields."""
        member = MemberCreate(name="Jane Doe")
        assert member.name == "Jane Doe"
        assert member.email is None
        assert member.phone is None

    def test_empty_name_fails(self):
        """Test that empty name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            MemberCreate(name="")
        assert "string_too_short" in str(exc_info.value)

    def test_missing_name_fails(self):
        """Test that missing name raises validation error."""
        with pytest.raises(ValidationError):
            MemberCreate()  # type: ignore

    def test_name_too_long_fails(self):
        """Test that name exceeding max length fails."""
        with pytest.raises(ValidationError) as exc_info:
            MemberCreate(name="x" * 256)
        assert "string_too_long" in str(exc_info.value)


class TestEntryCheckIn:
    """Tests for EntryCheckIn schema."""

    def test_valid_entry(self):
        """Test valid entry check-in."""
        entry = EntryCheckIn(member_id=1, notes="Court A")
        assert entry.member_id == 1
        assert entry.notes == "Court A"

    def test_valid_entry_without_notes(self):
        """Test valid entry check-in without notes."""
        entry = EntryCheckIn(member_id=1)
        assert entry.member_id == 1
        assert entry.notes is None

    def test_member_id_must_be_positive(self):
        """Test that member_id must be positive."""
        with pytest.raises(ValidationError) as exc_info:
            EntryCheckIn(member_id=0)
        assert "greater_than" in str(exc_info.value)

    def test_negative_member_id_fails(self):
        """Test that negative member_id fails."""
        with pytest.raises(ValidationError):
            EntryCheckIn(member_id=-1)

    def test_notes_max_length(self):
        """Test that notes exceeding max length fails."""
        with pytest.raises(ValidationError) as exc_info:
            EntryCheckIn(member_id=1, notes="x" * 256)
        assert "string_too_long" in str(exc_info.value)


class TestPaymentCheckIn:
    """Tests for PaymentCheckIn schema with amount validation."""

    def test_valid_payment(self):
        """Test valid payment."""
        payment = PaymentCheckIn(member_id=1, amount=Decimal("25.50"), notes="Test")
        assert payment.member_id == 1
        assert payment.amount == Decimal("25.50")
        assert payment.notes == "Test"

    def test_valid_payment_without_notes(self):
        """Test valid payment without notes."""
        payment = PaymentCheckIn(member_id=1, amount=Decimal("100.00"))
        assert payment.amount == Decimal("100.00")
        assert payment.notes is None

    def test_minimum_amount(self):
        """Test minimum valid amount (0.01)."""
        payment = PaymentCheckIn(member_id=1, amount=Decimal("0.01"))
        assert payment.amount == Decimal("0.01")

    def test_maximum_amount(self):
        """Test maximum valid amount (1000.00)."""
        payment = PaymentCheckIn(member_id=1, amount=Decimal("1000.00"))
        assert payment.amount == Decimal("1000.00")

    def test_zero_amount_fails(self):
        """Test that zero amount fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            PaymentCheckIn(member_id=1, amount=Decimal("0"))
        assert "greater_than" in str(exc_info.value)

    def test_negative_amount_fails(self):
        """Test that negative amount fails validation."""
        with pytest.raises(ValidationError):
            PaymentCheckIn(member_id=1, amount=Decimal("-10.00"))

    def test_amount_exceeds_maximum_fails(self):
        """Test that amount > 1000 fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            PaymentCheckIn(member_id=1, amount=Decimal("1000.01"))
        assert "less_than_equal" in str(exc_info.value)

    def test_amount_too_many_decimals_fails(self):
        """Test that amount with > 2 decimal places fails."""
        with pytest.raises(ValidationError) as exc_info:
            PaymentCheckIn(member_id=1, amount=Decimal("25.555"))
        assert "2 decimal places" in str(exc_info.value)

    def test_amount_with_one_decimal_place_valid(self):
        """Test that amount with 1 decimal place is valid."""
        payment = PaymentCheckIn(member_id=1, amount=Decimal("25.5"))
        # Should be normalized to 2 decimal places
        assert payment.amount == Decimal("25.50")

    def test_amount_integer_valid(self):
        """Test that integer amount is valid."""
        payment = PaymentCheckIn(member_id=1, amount=Decimal("100"))
        assert payment.amount == Decimal("100.00")

    @pytest.mark.parametrize(
        "amount",
        [
            Decimal("0.01"),
            Decimal("1.00"),
            Decimal("50.50"),
            Decimal("100.00"),
            Decimal("500.00"),
            Decimal("999.99"),
            Decimal("1000.00"),
        ],
    )
    def test_valid_amounts(self, amount: Decimal):
        """Test various valid amounts."""
        payment = PaymentCheckIn(member_id=1, amount=amount)
        assert payment.amount == amount.quantize(Decimal("0.01"))

    @pytest.mark.parametrize(
        "amount,error_type",
        [
            (Decimal("0"), "greater_than"),
            (Decimal("-1"), "greater_than"),
            (Decimal("1001"), "less_than_equal"),
            (Decimal("0.001"), "2 decimal places"),
        ],
    )
    def test_invalid_amounts(self, amount: Decimal, error_type: str):
        """Test various invalid amounts."""
        with pytest.raises(ValidationError) as exc_info:
            PaymentCheckIn(member_id=1, amount=amount)
        assert error_type in str(exc_info.value)

    def test_amount_1000_001_fails_max_check_first(self):
        """Test that 1000.001 fails (may fail max or decimal check depending on validation order)."""
        with pytest.raises(ValidationError):
            PaymentCheckIn(member_id=1, amount=Decimal("1000.001"))
