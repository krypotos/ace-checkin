# Quick Start Guide ⚡

Get Ace Check-in running in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- OR: Python 3.11+ and PostgreSQL

## Option 1: Docker (Fastest)

```bash
# 1. Clone and navigate
git clone <repository-url>
cd ace-checkin

# 2. Start all services
docker-compose up

# 3. In another terminal, run migrations
docker-compose exec app alembic upgrade head

# 4. Verify it works
curl http://localhost:8000/health

# 5. Access the API
# Documentation: http://localhost:8000/docs
```

Done! Your API is running. 🚀

## Option 2: Local Python Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure PostgreSQL
# Make sure PostgreSQL is running, then:
createdb ace_checkin

# 4. Run migrations
alembic upgrade head

# 5. Start server
uvicorn app.main:app --reload

# 6. Access the API
# Documentation: http://localhost:8000/docs
```

## First Steps

### 1. Create a Member

```bash
curl -X POST http://localhost:8000/api/members \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com"
  }'
```

### 2. Record an Entry

Barcode-friendly (GET):
```bash
curl "http://localhost:8000/api/entry/checkin/M001?notes=Court+A"
```

Or via POST (for applications):
```bash
curl -X POST http://localhost:8000/api/entry \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "M001",
    "notes": "Court A"
  }'
```

### 3. Record a Payment

Barcode-friendly (GET):
```bash
curl "http://localhost:8000/api/payment/checkin/M001?amount=25.50&notes=Monthly+fee"
```

Or via POST (for applications):
```bash
curl -X POST http://localhost:8000/api/payment \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "M001",
    "amount": 25.50,
    "notes": "Monthly fee"
  }'
```

### 4. View Payment Summary

```bash
curl http://localhost:8000/api/payment/summary/M001
```

## API Documentation

Interactive API docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Barcode/QR Code Integration

The system supports barcode scanning! Create QR codes that link to:

**For Check-in:**
```
https://yourdomain.com/api/entry/checkin/{member_id}
```

**For Payment:**
```
https://yourdomain.com/api/payment/checkin/{member_id}?amount=25.50
```

When a member scans a QR code with their barcode scanner app or mobile device, it automatically logs the entry or payment.

## Populate Sample Data

```bash
# With Docker
docker-compose exec app python3 scripts/seed_initial_data.py

# Locally
python3 scripts/seed_initial_data.py
```

## Run Tests

```bash
# Make the test script executable
chmod +x test_api.sh

# Run automated tests
./test_api.sh
```

## Common Issues

### Port 8000 already in use?

```bash
# Change port in docker-compose.yml or run:
uvicorn app.main:app --port 8001 --reload
```

### Database connection error?

```bash
# With Docker, restart services
docker-compose down
docker-compose up

# Locally, check PostgreSQL is running
psql --version
```

### Need to reset everything?

```bash
# With Docker (WARNING: deletes data)
docker-compose down -v
docker-compose up
docker-compose exec app alembic upgrade head

# Locally
dropdb ace_checkin
createdb ace_checkin
alembic upgrade head
```

## Project Structure

```
ace-checkin/
├── app/              # FastAPI application
├── alembic/          # Database migrations
├── nginx/            # Nginx configuration
├── docker-compose.yml # Docker setup
└── README.md         # Full documentation
```

## Next Steps

1. **Read Full Docs**: Check `README.md` for complete API reference
2. **Development**: See `DEVELOPMENT.md` for development guide
3. **Deployment**: See `DEPLOYMENT.md` for production setup on DigitalOcean
4. **Customize**: Modify `app/main.py` and `app/models.py` as needed

## Useful Commands

```bash
# View logs
docker-compose logs -f app

# Access database
docker-compose exec db psql -U ace_user -d ace_checkin

# Run migrations
docker-compose exec app alembic upgrade head

# Stop everything
docker-compose down

# Start in background
docker-compose up -d

# Stop services
docker-compose stop
```

## API Endpoints at a Glance

```
Health & Status
  GET  /health                    - Health check

Members
  POST /api/members               - Create member
  GET  /api/members               - List all members
  GET  /api/members/{member_id}   - Get member details

Entry (Check-in)
  POST /api/entry                 - Record entry
  GET  /api/entry/{member_id}     - List entries for member

Payment
  POST /api/payment               - Record payment
  GET  /api/payment/{member_id}   - List payments for member
  GET  /api/payment/summary/{member_id} - Payment summary
```

## Example Workflow

```bash
# 1. Create members
curl -X POST http://localhost:8000/api/members -H "Content-Type: application/json" \
  -d '{"member_id": "M001", "name": "Alice", "email": "alice@example.com"}'

curl -X POST http://localhost:8000/api/members -H "Content-Type: application/json" \
  -d '{"member_id": "M002", "name": "Bob", "email": "bob@example.com"}'

# 2. Members check in
curl -X POST http://localhost:8000/api/entry -H "Content-Type: application/json" \
  -d '{"member_id": "M001", "notes": "Morning session"}'

curl -X POST http://localhost:8000/api/entry -H "Content-Type: application/json" \
  -d '{"member_id": "M002", "notes": "Evening session"}'

# 3. Members pay
curl -X POST http://localhost:8000/api/payment -H "Content-Type: application/json" \
  -d '{"member_id": "M001", "amount": 30, "notes": "Court rental"}'

# 4. Check summaries
curl http://localhost:8000/api/payment/summary/M001
curl http://localhost:8000/api/entry/M002
```

## Barcode Integration

The system is designed for barcode scanning from mobile devices:

1. Create QR codes linking to:
   - Entry: `https://yourdomain.com/api/entry`
   - Payment: `https://yourdomain.com/api/payment`

2. Mobile device scans → submits member_id (and amount for payment)

3. System records instantly

For deployment on DigitalOcean, see `DEPLOYMENT.md`.

---

**Questions?** Check the full documentation or create an issue on GitHub.

**Ready to deploy?** See `DEPLOYMENT.md` for DigitalOcean setup.
