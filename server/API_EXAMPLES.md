# API Usage Examples 📚

Complete examples of using the Ace Check-in API.

## Base URL

```
Development: http://localhost:8000
Production: https://yourdomain.com
```

## Authentication

Currently, the API is public (no authentication required). This will be added in a future version.

## Response Format

All responses are JSON:
```json
{
  "id": 1,
  "member_id": "M001",
  "name": "John Doe",
  ...
}
```

## Error Responses

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Health Check

### Check API Status

```bash
curl http://localhost:8000/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "environment": "development"
}
```

---

## Member Management

### Create a Member

**Request:**
```bash
curl -X POST http://localhost:8000/api/members \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "M001",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-0001"
  }'
```

**Response (200 OK):**
```json
{
  "id": 1,
  "member_id": "M001",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-0001",
  "created_at": "2024-01-15T10:30:00"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "Member with ID 'M001' already exists"
}
```

### Get a Specific Member

**Request:**
```bash
curl http://localhost:8000/api/members/M001
```

**Response (200 OK):**
```json
{
  "id": 1,
  "member_id": "M001",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-0001",
  "created_at": "2024-01-15T10:30:00"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Member with ID 'INVALID' not found"
}
```

### List All Members

**Request:**
```bash
# Without pagination (all members)
curl http://localhost:8000/api/members

# With pagination
curl 'http://localhost:8000/api/members?skip=0&limit=10'
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "member_id": "M001",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-0001",
    "created_at": "2024-01-15T10:30:00"
  },
  {
    "id": 2,
    "member_id": "M002",
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "+1-555-0002",
    "created_at": "2024-01-15T10:35:00"
  }
]
```

### Pagination Parameters

- `skip` (int, default: 0) - Number of records to skip
- `limit` (int, default: 100) - Maximum records to return

**Example:**
```bash
curl 'http://localhost:8000/api/members?skip=20&limit=10'
```

---

## Entry Management (Check-ins)

### Record a Member Entry (GET - Barcode Scanner Friendly)

**Request:**
```bash
# Simple check-in
curl http://localhost:8000/api/entry/checkin/M001

# With optional notes
curl "http://localhost:8000/api/entry/checkin/M001?notes=Court+A"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "member_id": "M001",
  "timestamp": "2024-01-15T10:45:30",
  "notes": "Court A"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Member with ID 'INVALID' not found"
}
```

### Record a Member Entry (POST - API/Application Use)

**Request:**
```bash
curl -X POST http://localhost:8000/api/entry \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "M001",
    "notes": "Court A - Morning session"
  }'
```

**Response (200 OK):**
```json
{
  "id": 1,
  "member_id": "M001",
  "timestamp": "2024-01-15T10:45:30",
  "notes": "Court A - Morning session"
}
```

**Note:** Use the GET endpoint for barcode scanners, POST for applications.

### Get Member Entry History

**Request:**
```bash
# All entries for a member
curl http://localhost:8000/api/entry/M001

# With pagination
curl 'http://localhost:8000/api/entry/M001?skip=0&limit=20'

# Latest 10 entries
curl 'http://localhost:8000/api/entry/M001?limit=10'
```

**Response (200 OK):**
```json
[
  {
    "id": 3,
    "member_id": "M001",
    "timestamp": "2024-01-15T16:30:00",
    "notes": "Evening session"
  },
  {
    "id": 2,
    "member_id": "M001",
    "timestamp": "2024-01-15T13:15:00",
    "notes": "Afternoon session"
  },
  {
    "id": 1,
    "member_id": "M001",
    "timestamp": "2024-01-15T10:45:30",
    "notes": "Morning session"
  }
]
```

**Note:** Results are sorted by timestamp (newest first).

### Entry Scenarios

**Quick Entry (without notes):**
```bash
curl -X POST http://localhost:8000/api/entry \
  -H "Content-Type: application/json" \
  -d '{"member_id": "M001"}'
```

**Entry with Court Information:**
```bash
curl -X POST http://localhost:8000/api/entry \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "M001",
    "notes": "Court 3 - Singles"
  }'
```

---

## Payment Management

### Record a Payment (GET - Barcode Scanner Friendly)

**Request:**
```bash
# Simple payment
curl "http://localhost:8000/api/payment/checkin/M001?amount=25.50"

# With optional notes
curl "http://localhost:8000/api/payment/checkin/M001?amount=25.50&notes=Monthly+fee"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "member_id": "M001",
  "amount": 2550,
  "timestamp": "2024-01-15T11:00:00",
  "notes": "Monthly fee"
}
```

**Note:** Amount 2550 = $25.50 (stored in cents)

### Record a Payment (POST - API/Application Use)

**Request:**
```bash
curl -X POST http://localhost:8000/api/payment \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "M001",
    "amount": 25.50,
    "notes": "Monthly court rental"
  }'
```

**Response (200 OK):**
```json
{
  "id": 1,
  "member_id": "M001",
  "amount": 2550,
  "timestamp": "2024-01-15T11:00:00",
  "notes": "Monthly court rental"
}
```

**Note:** Use the GET endpoint for barcode scanners, POST for applications.

### Get Member Payment History

**Request:**
```bash
# All payments for a member
curl http://localhost:8000/api/payment/M001

# With pagination
curl 'http://localhost:8000/api/payment/M001?skip=0&limit=50'
```

**Response (200 OK):**
```json
[
  {
    "id": 5,
    "member_id": "M001",
    "amount": 2550,
    "timestamp": "2024-01-15T14:00:00",
    "notes": "Additional payment"
  },
  {
    "id": 4,
    "member_id": "M001",
    "amount": 5000,
    "timestamp": "2024-01-08T10:00:00",
    "notes": "Monthly court rental"
  },
  {
    "id": 1,
    "member_id": "M001",
    "amount": 2550,
    "timestamp": "2024-01-01T09:00:00",
    "notes": "Monthly court rental"
  }
]
```

### Get Payment Summary

**Request:**
```bash
curl http://localhost:8000/api/payment/summary/M001
```

**Response (200 OK):**
```json
{
  "member_id": "M001",
  "member_name": "John Doe",
  "total_payments": 5,
  "total_amount": 130.00,
  "last_payment": "2024-01-15T14:00:00"
}
```

### Payment Scenarios

**One-time Payment:**
```bash
curl -X POST http://localhost:8000/api/payment \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "M001",
    "amount": 50.00,
    "notes": "One-time court rental"
  }'
```

**Monthly Subscription:**
```bash
curl -X POST http://localhost:8000/api/payment \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "M001",
    "amount": 99.99,
    "notes": "January - Monthly subscription"
  }'
```

**Partial Payment:**
```bash
curl -X POST http://localhost:8000/api/payment \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "M001",
    "amount": 12.50,
    "notes": "Partial payment for balance"
  }'
```

---

## Complete Workflow Examples

### Example 1: New Member Registration and First Entry

```bash
# Step 1: Create member
curl -X POST http://localhost:8000/api/members \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "M100",
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "phone": "+1-555-0100"
  }'

# Step 2: Member checks in
curl -X POST http://localhost:8000/api/entry \
  -H "Content-Type: application/json" \
  -d '{"member_id": "M100", "notes": "Court B"}'

# Step 3: Member pays for the session
curl -X POST http://localhost:8000/api/payment \
  -H "Content-Type: application/json" \
  -d '{"member_id": "M100", "amount": 25.00, "notes": "Court rental"}'

# Step 4: Verify payment
curl http://localhost:8000/api/payment/summary/M100
```

### Example 2: Track Multiple Members Over a Day

```bash
# Create multiple members
MEMBERS=("M201" "M202" "M203")
NAMES=("Bob Smith" "Carol White" "David Green")

for i in "${!MEMBERS[@]}"; do
  curl -X POST http://localhost:8000/api/members \
    -H "Content-Type: application/json" \
    -d "{
      \"member_id\": \"${MEMBERS[$i]}\",
      \"name\": \"${NAMES[$i]}\",
      \"email\": \"${MEMBERS[$i]}@example.com\"
    }"
done

# Members check in throughout the day
for member_id in "${MEMBERS[@]}"; do
  curl -X POST http://localhost:8000/api/entry \
    -H "Content-Type: application/json" \
    -d "{\"member_id\": \"$member_id\", \"notes\": \"Morning session\"}"
done

# Members pay
for member_id in "${MEMBERS[@]}"; do
  curl -X POST http://localhost:8000/api/payment \
    -H "Content-Type: application/json" \
    -d "{\"member_id\": \"$member_id\", \"amount\": 30.00}"
done

# Get summary for all
for member_id in "${MEMBERS[@]}"; do
  curl http://localhost:8000/api/payment/summary/$member_id
done
```

### Example 3: Using with Python Requests Library

```python
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Create member
member_data = {
    "member_id": "M300",
    "name": "Python User",
    "email": "python@example.com"
}
response = requests.post(f"{BASE_URL}/api/members", json=member_data)
print(f"Member created: {response.json()}")

# Record entry
entry_data = {
    "member_id": "M300",
    "notes": "Python script entry"
}
response = requests.post(f"{BASE_URL}/api/entry", json=entry_data)
print(f"Entry recorded: {response.json()}")

# Record payment
payment_data = {
    "member_id": "M300",
    "amount": 50.00,
    "notes": "Payment from Python script"
}
response = requests.post(f"{BASE_URL}/api/payment", json=payment_data)
print(f"Payment recorded: {response.json()}")

# Get summary
response = requests.get(f"{BASE_URL}/api/payment/summary/M300")
summary = response.json()
print(f"Payment Summary: {json.dumps(summary, indent=2)}")
```

---

## Query Parameters Reference

### Pagination Parameters (List Endpoints)

| Parameter | Type | Default | Example |
|-----------|------|---------|---------|
| `skip` | int | 0 | `?skip=10` |
| `limit` | int | 100 | `?limit=50` |

**Example:**
```bash
# Get items 11-20
curl 'http://localhost:8000/api/members?skip=10&limit=10'

# Get last 5 items
curl 'http://localhost:8000/api/entry/M001?skip=0&limit=5'
```

---

## API Limits & Constraints

### Input Validation

| Field | Constraint | Example |
|-------|-----------|---------|
| `member_id` | 1-50 chars, alphanumeric + special | M001, MEMBER-123 |
| `name` | 1-255 chars | John Doe |
| `email` | Valid email format | john@example.com |
| `phone` | 1-20 chars | +1-555-0001 |
| `amount` | > 0, 2 decimal places | 25.50, 100.00 |
| `notes` | 0-255 chars (optional) | Court A |

### Rate Limiting

Currently: No rate limiting (will be added in future versions)

### Maximum Response Size

Currently: No hard limit on response size (will be added in future versions)

---

## HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK - Request succeeded | Successful GET/POST |
| 400 | Bad Request - Invalid input | Duplicate member ID |
| 404 | Not Found - Resource doesn't exist | Member not found |
| 422 | Validation Error - Invalid data format | Invalid email format |
| 500 | Server Error - Internal issue | Database connection error |

---

## Common Error Scenarios

### Duplicate Member

**Request:**
```bash
curl -X POST http://localhost:8000/api/members \
  -H "Content-Type: application/json" \
  -d '{"member_id":"M001","name":"John"}'
```

**Response (400 Bad Request):**
```json
{
  "detail": "Member with ID 'M001' already exists"
}
```

### Member Not Found

**Request:**
```bash
curl http://localhost:8000/api/members/INVALID
```

**Response (404 Not Found):**
```json
{
  "detail": "Member with ID 'INVALID' not found"
}
```

### Invalid Data Format

**Request:**
```bash
curl -X POST http://localhost:8000/api/members \
  -H "Content-Type: application/json" \
  -d '{"member_id":"","name":"John"}'
```

**Response (422 Validation Error):**
```json
{
  "detail": [
    {
      "loc": ["body", "member_id"],
      "msg": "ensure this value has at least 1 character",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

---

## Testing the API

### Using cURL

```bash
# Test all endpoints
./test_api.sh

# Test specific endpoint
curl -v http://localhost:8000/health
```

### Using Swagger UI

1. Navigate to `http://localhost:8000/docs`
2. Click on an endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

### Using Python

```python
import requests

# Test health
response = requests.get("http://localhost:8000/health")
print(response.status_code)  # Should be 200
print(response.json())
```

---

## API Documentation

### Interactive Swagger UI
http://localhost:8000/docs

### Alternative ReDoc UI
http://localhost:8000/redoc

### OpenAPI Schema
http://localhost:8000/openapi.json

---

## Tips & Best Practices

1. **Always include Content-Type header** for POST requests
2. **Use meaningful member_id values** (e.g., barcode numbers)
3. **Add descriptive notes** for context
4. **Store responses** for audit trail
5. **Implement exponential backoff** for retries
6. **Validate input** before sending
7. **Use pagination** for large lists
8. **Cache frequently accessed data** when possible

---

## Support

For API questions:
1. Check the interactive documentation at `/docs`
2. Review complete documentation in `README.md`
3. See examples in this file
4. Check project on GitHub for issues/discussions

---

**Last Updated:** 2024-01-15
**API Version:** 1.0.0
