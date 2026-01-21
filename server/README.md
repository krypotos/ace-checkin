# Ace Check-in System 🎾

A modern web application for tracking member entries and payments at a tennis club.

## Features

- ✅ Member management (create, view, list)
- ✅ Entry logging (track when members enter the court)
- ✅ Payment logging (track member payments)
- ✅ RESTful API with automatic documentation
- ✅ PostgreSQL database with Alembic migrations
- ✅ Docker & Docker Compose for easy deployment
- ✅ Nginx reverse proxy
- ✅ Barcode scanning support via mobile devices

## Technology Stack

- **Backend**: FastAPI with SQLModel
- **Database**: PostgreSQL
- **Migrations**: Alembic
- **Server**: Uvicorn (ASGI)
- **Reverse Proxy**: Nginx
- **Containerization**: Docker & Docker Compose
- **Python**: 3.11+

## Project Structure

```
ace-checkin/
├── app/                          # Application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI application
│   ├── models.py                 # SQLModel database models
│   ├── schemas.py                # Pydantic request/response schemas
│   ├── config.py                 # Configuration management
│   └── database.py               # Database setup and sessions
├── alembic/                      # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                 # Migration files
│       └── 001_initial_schema.py
├── nginx/                        # Nginx configuration
│   ├── nginx.conf
│   └── conf.d/
│       └── default.conf
├── docker-compose.yml            # Docker Compose configuration
├── Dockerfile                    # Docker image definition
├── requirements.txt              # Python dependencies
├── alembic.ini                   # Alembic configuration
└── README.md                     # This file
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Or: Python 3.11+, PostgreSQL 16+

### Local Development with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ace-checkin
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Start the application**
   ```bash
   docker-compose up
   ```

4. **Access the application**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - API Documentation (ReDoc): http://localhost:8000/redoc
   - Nginx Proxy: http://localhost

### Local Development Without Docker

1. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your local database credentials
   ```

4. **Create database**
   ```bash
   createdb -U postgres ace_checkin
   ```

5. **Run migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the server**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Access the application**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## API Endpoints

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "environment": "development"
}
```

### Member Management

#### Create Member
```bash
POST /api/members
Content-Type: application/json

{
  "member_id": "12345",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-1234"
}
```

Response:
```json
{
  "id": 1,
  "member_id": "12345",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-1234",
  "created_at": "2024-01-01T12:00:00"
}
```

#### Get Member
```bash
GET /api/members/{member_id}
```

#### List Members
```bash
GET /api/members?skip=0&limit=100
```

### Entry Management

#### Check-in (Record Entry)
```bash
POST /api/entry
Content-Type: application/json

{
  "member_id": "12345",
  "notes": "Court A"
}
```

Response:
```json
{
  "id": 1,
  "member_id": "12345",
  "timestamp": "2024-01-01T12:00:00",
  "notes": "Court A"
}
```

#### Get Member Entries
```bash
GET /api/entry/{member_id}?skip=0&limit=100
```

### Payment Management

#### Record Payment
```bash
POST /api/payment
Content-Type: application/json

{
  "member_id": "12345",
  "amount": 25.50,
  "notes": "Monthly fee"
}
```

Response:
```json
{
  "id": 1,
  "member_id": "12345",
  "amount": 2550,
  "timestamp": "2024-01-01T12:00:00",
  "notes": "Monthly fee"
}
```

#### Get Member Payments
```bash
GET /api/payment/{member_id}?skip=0&limit=100
```

#### Get Payment Summary
```bash
GET /api/payment/summary/{member_id}
```

Response:
```json
{
  "member_id": "12345",
  "member_name": "John Doe",
  "total_payments": 5,
  "total_amount": 127.50,
  "last_payment": "2024-01-01T12:00:00"
}
```

## Barcode Integration

The system supports barcode scanning via QR codes from mobile devices. Barcode readers can only follow links (GET requests), so we provide GET endpoints specifically for this purpose.

### For Entry Check-in
Create a QR code that links to:
```
https://your-domain.com/api/entry/checkin/{member_id}
```

Or with optional notes (court information):
```
https://your-domain.com/api/entry/checkin/{member_id}?notes=Court+A
```

Example: `https://your-domain.com/api/entry/checkin/M001?notes=Court+A`

### For Payment
Create a QR code that links to:
```
https://your-domain.com/api/payment/checkin/{member_id}?amount={amount}
```

Or with optional payment notes:
```
https://your-domain.com/api/payment/checkin/{member_id}?amount={amount}&notes=Monthly+fee
```

Examples:
- `https://your-domain.com/api/payment/checkin/M001?amount=25.50`
- `https://your-domain.com/api/payment/checkin/M001?amount=25.50&notes=Court+rental`

### Alternative: POST Endpoints (For Applications)
For programmatic access from applications or APIs, use POST requests:

**Entry:**
```bash
POST /api/entry
```

**Payment:**
```bash
POST /api/payment
```

See [API_EXAMPLES.md](API_EXAMPLES.md) for POST examples.

## Database Migrations with Alembic

### Run Migrations
```bash
# Inside Docker
docker-compose exec app alembic upgrade head

# Locally
alembic upgrade head
```

### Create New Migration
```bash
# Auto-generate migration (detects schema changes)
docker-compose exec app alembic revision --autogenerate -m "Description of changes"

# Or manually
docker-compose exec app alembic revision -m "Description of changes"
```

### View Migration History
```bash
docker-compose exec app alembic history
```

### Downgrade Database
```bash
# Go back one version
docker-compose exec app alembic downgrade -1

# Or to a specific revision
docker-compose exec app alembic downgrade 001
```

## Docker Deployment

### Local Development
```bash
docker-compose up
```

### Production Deployment on DigitalOcean

1. **Create a Droplet**
   - Ubuntu 22.04 LTS
   - Recommended: 2GB RAM, 50GB SSD

2. **Install Docker**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

3. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd ace-checkin
   ```

4. **Configure Environment**
   ```bash
   # Create secure .env file
   cat > .env << EOF
   DB_USER=ace_user
   DB_PASSWORD=your-secure-password
   DB_NAME=ace_checkin
   ENVIRONMENT=production
   EOF
   chmod 600 .env
   ```

5. **Start Services**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

6. **Set up SSL Certificate (using Let's Encrypt)**
   ```bash
   # Install certbot
   sudo apt-get install certbot python3-certbot-nginx

   # Generate certificate
   sudo certbot certonly --standalone -d your-domain.com

   # Copy certificate to nginx
   sudo mkdir -p nginx/ssl
   sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
   sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
   ```

7. **Enable HTTPS in Nginx**
   - Uncomment HTTPS server block in `nginx/conf.d/default.conf`
   - Update domain name
   - Restart: `docker-compose restart nginx`

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Database Configuration
DB_USER=ace_user                 # PostgreSQL username
DB_PASSWORD=secure_password      # PostgreSQL password
DB_NAME=ace_checkin              # Database name
DB_HOST=db                       # Database host (db for Docker)
DB_PORT=5432                     # PostgreSQL port

# Application Settings
ENVIRONMENT=development          # development or production
```

## Useful Commands

### Docker Compose

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f app

# Run migrations
docker-compose exec app alembic upgrade head

# Access database
docker-compose exec db psql -U ace_user -d ace_checkin

# Rebuild image
docker-compose build
```

### Database Management

```bash
# Connect to database
psql -h localhost -U ace_user -d ace_checkin

# List tables
\dt

# Exit
\q
```

## API Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Create Member
```bash
curl -X POST http://localhost:8000/api/members \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "123456",
    "name": "Test Member",
    "email": "test@example.com"
  }'
```

### Record Entry
```bash
curl -X POST http://localhost:8000/api/entry \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "123456",
    "notes": "Court A"
  }'
```

### Record Payment
```bash
curl -X POST http://localhost:8000/api/payment \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "123456",
    "amount": 25.50,
    "notes": "Monthly fee"
  }'
```

## Security Considerations

For production deployment:

1. **Enable HTTPS**
   - Use Let's Encrypt for SSL certificates
   - Redirect HTTP to HTTPS in Nginx

2. **Secure Environment Variables**
   - Use strong database passwords
   - Use secrets management (e.g., Docker secrets)
   - Never commit `.env` files

3. **Database Security**
   - Use strong passwords
   - Restrict database access
   - Enable PostgreSQL authentication

4. **API Security**
   - Add authentication/authorization (JWT, OAuth2)
   - Rate limiting
   - CORS configuration (currently allows all)
   - Input validation

5. **Monitoring**
   - Set up logging
   - Monitor resource usage
   - Set up alerts

## Troubleshooting

### Database Connection Errors
```bash
# Check if PostgreSQL is running
docker-compose logs db

# Verify connection string in .env
# Test connection
docker-compose exec app python3 -c "from app.database import engine; engine.connect()"
```

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Or change port in docker-compose.yml
```

### Migration Issues
```bash
# Check migration history
docker-compose exec app alembic history

# Downgrade and upgrade again
docker-compose exec app alembic downgrade -1
docker-compose exec app alembic upgrade head
```

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test
3. Commit: `git commit -am 'Add feature'`
4. Push: `git push origin feature/your-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions, please open an issue on GitHub or contact the development team.

## Roadmap

- [ ] Authentication & Authorization (JWT)
- [ ] Mobile app for barcode scanning
- [ ] Admin dashboard
- [ ] Reporting and analytics
- [ ] SMS/Email notifications
- [ ] Membership status tracking
- [ ] Advanced scheduling features
- [ ] Payment integration (Stripe, PayPal)

---

**Happy coding! 🚀**
