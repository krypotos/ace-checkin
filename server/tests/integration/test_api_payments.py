"""
Integration tests for Payment API endpoints.

These tests verify the payment logging functionality including amount validation.
"""

from fastapi.testclient import TestClient

from app.models import Member, PaymentLog


class TestPaymentEndpoints:
    """Tests for /api/payment endpoints."""

    def test_log_payment_success(self, client: TestClient, sample_member: Member):
        """Test successful payment logging."""
        response = client.post(
            "/api/payment",
            json={"member_id": sample_member.id, "amount": 25.50, "notes": "Court fee"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["member_id"] == sample_member.id
        assert data["member_name"] == sample_member.name
        assert data["amount"] == "25.50"  # Decimal serialized as string
        assert data["notes"] == "Court fee"
        assert "$25.50" in data["message"]
        assert "id" in data
        assert "timestamp" in data

    def test_log_payment_without_notes(self, client: TestClient, sample_member: Member):
        """Test payment logging without notes."""
        response = client.post(
            "/api/payment",
            json={"member_id": sample_member.id, "amount": 100.00},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["notes"] is None

    def test_log_payment_minimum_amount(self, client: TestClient, sample_member: Member):
        """Test payment with minimum amount (0.01)."""
        response = client.post(
            "/api/payment",
            json={"member_id": sample_member.id, "amount": 0.01},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == "0.01"

    def test_log_payment_maximum_amount(self, client: TestClient, sample_member: Member):
        """Test payment with maximum amount (1000.00)."""
        response = client.post(
            "/api/payment",
            json={"member_id": sample_member.id, "amount": 1000.00},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == "1000.00"

    def test_log_payment_zero_amount_fails(self, client: TestClient, sample_member: Member):
        """Test that zero amount fails."""
        response = client.post(
            "/api/payment",
            json={"member_id": sample_member.id, "amount": 0},
        )

        assert response.status_code == 422
        assert "greater_than" in str(response.json())

    def test_log_payment_negative_amount_fails(self, client: TestClient, sample_member: Member):
        """Test that negative amount fails."""
        response = client.post(
            "/api/payment",
            json={"member_id": sample_member.id, "amount": -10.00},
        )

        assert response.status_code == 422

    def test_log_payment_exceeds_max_fails(self, client: TestClient, sample_member: Member):
        """Test that amount > 1000 fails."""
        response = client.post(
            "/api/payment",
            json={"member_id": sample_member.id, "amount": 1000.01},
        )

        assert response.status_code == 422
        assert "less_than_equal" in str(response.json())

    def test_log_payment_too_many_decimals_fails(self, client: TestClient, sample_member: Member):
        """Test that amount with > 2 decimal places fails."""
        response = client.post(
            "/api/payment",
            json={"member_id": sample_member.id, "amount": 25.555},
        )

        assert response.status_code == 422
        assert "decimal" in str(response.json()).lower()

    def test_log_payment_member_not_found(self, client: TestClient):
        """Test payment logging for non-existent member."""
        response = client.post(
            "/api/payment",
            json={"member_id": 99999, "amount": 25.00},
        )

        assert response.status_code == 404

    def test_get_member_payments_success(
        self, client: TestClient, sample_member: Member, sample_payment: PaymentLog
    ):
        """Test getting payment history for a member."""
        response = client.get(f"/api/payments/{sample_member.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["member_id"] == sample_member.id
        assert data["member_name"] == sample_member.name
        assert data["total_payments"] == 1
        assert len(data["payments"]) == 1
        assert data["total_amount"] == 25.50  # From sample_payment fixture

    def test_get_member_payments_empty(self, client: TestClient, sample_member: Member):
        """Test getting payments when member has no payments."""
        response = client.get(f"/api/payments/{sample_member.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["total_payments"] == 0
        assert data["total_amount"] == 0
        assert data["payments"] == []

    def test_get_member_payments_not_found(self, client: TestClient):
        """Test getting payments for non-existent member."""
        response = client.get("/api/payments/99999")

        assert response.status_code == 404

    def test_multiple_payments_total(self, client: TestClient, sample_member: Member):
        """Test that multiple payments are summed correctly."""
        # Log multiple payments
        amounts = [10.00, 20.50, 30.00]
        for amount in amounts:
            response = client.post(
                "/api/payment",
                json={"member_id": sample_member.id, "amount": amount},
            )
            assert response.status_code == 200

        # Verify total
        response = client.get(f"/api/payments/{sample_member.id}")
        data = response.json()
        assert data["total_payments"] == 3
        assert data["total_amount"] == sum(amounts)


class TestMemberSummaryEndpoint:
    """Tests for /api/member/{id}/summary endpoint."""

    def test_member_summary_success(
        self,
        client: TestClient,
        sample_member: Member,
        sample_entry: PaymentLog,
        sample_payment: PaymentLog,
    ):
        """Test getting member summary with entries and payments."""
        response = client.get(f"/api/member/{sample_member.id}/summary")

        assert response.status_code == 200
        data = response.json()

        # Check member info
        assert data["member"]["id"] == sample_member.id
        assert data["member"]["name"] == sample_member.name

        # Check stats
        assert data["stats"]["total_entries"] == 1
        assert data["stats"]["total_payments"] == 1
        assert data["stats"]["total_amount_paid"] == 25.50

    def test_member_summary_empty_stats(self, client: TestClient, sample_member: Member):
        """Test member summary with no entries or payments."""
        response = client.get(f"/api/member/{sample_member.id}/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["stats"]["total_entries"] == 0
        assert data["stats"]["total_payments"] == 0
        assert data["stats"]["total_amount_paid"] == 0
        assert data["stats"]["last_entry"] is None
        assert data["stats"]["last_payment"] is None

    def test_member_summary_not_found(self, client: TestClient):
        """Test member summary for non-existent member."""
        response = client.get("/api/member/99999/summary")

        assert response.status_code == 404
