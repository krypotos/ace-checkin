#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="${1:-http://localhost:8000}"

echo -e "${YELLOW}Testing Ace Check-in API${NC}"
echo "Base URL: $BASE_URL"
echo "=========================================="

# Function to make requests and check status
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local expected_status=$4

    echo -e "\n${YELLOW}Testing: $method $endpoint${NC}"

    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ Status: $http_code${NC}"
    else
        echo -e "${RED}✗ Status: $http_code (expected $expected_status)${NC}"
    fi

    echo "Response:"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
}

# Test 1: Health Check
test_endpoint "GET" "/health" "" "200"

# Test 2: List Members (initially empty)
test_endpoint "GET" "/api/members" "" "200"

# Test 3: Create Member
MEMBER_PAYLOAD='{"member_id":"TEST001","name":"Test Member","email":"test@example.com","phone":"+1-555-0000"}'
test_endpoint "POST" "/api/members" "$MEMBER_PAYLOAD" "200"

# Test 4: Get Member
test_endpoint "GET" "/api/members/TEST001" "" "200"

# Test 5: Create Entry (GET - Barcode Scanner Friendly)
test_endpoint "GET" "/api/entry/checkin/TEST001" "" "200"

# Test 5b: Create Entry with notes
test_endpoint "GET" "/api/entry/checkin/TEST001?notes=Court+A" "" "200"

# Test 6: Get Member Entries
test_endpoint "GET" "/api/entry/TEST001" "" "200"

# Test 7: Create Payment (GET - Barcode Scanner Friendly)
test_endpoint "GET" "/api/payment/checkin/TEST001?amount=25.50" "" "200"

# Test 7b: Create Payment with notes
test_endpoint "GET" "/api/payment/checkin/TEST001?amount=25.50&notes=Monthly+fee" "" "200"

# Test 8: Get Member Payments
test_endpoint "GET" "/api/payment/TEST001" "" "200"

# Test 8b: Alternative - Create Entry via POST (for API use)
ENTRY_PAYLOAD='{"member_id":"TEST001","notes":"Afternoon session"}'
test_endpoint "POST" "/api/entry" "$ENTRY_PAYLOAD" "200"

# Test 8c: Alternative - Create Payment via POST (for API use)
PAYMENT_PAYLOAD='{"member_id":"TEST001","amount":30.00,"notes":"Additional payment"}'
test_endpoint "POST" "/api/payment" "$PAYMENT_PAYLOAD" "200"

# Test 9: Get Payment Summary
test_endpoint "GET" "/api/payment/summary/TEST001" "" "200"

# Test 10: Error - Member Not Found
test_endpoint "GET" "/api/members/NONEXISTENT" "" "404"

# Test 11: Error - Create Duplicate Member
test_endpoint "POST" "/api/members" "$MEMBER_PAYLOAD" "400"

echo -e "\n${YELLOW}=========================================="
echo "Testing Complete!${NC}"
