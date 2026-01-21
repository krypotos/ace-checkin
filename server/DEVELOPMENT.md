# Development Guide 🛠️

Complete guide for setting up a local development environment.

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 16+ (or Docker)
- Docker & Docker Compose (optional, recommended)
- Git
- Code Editor (VS Code, PyCharm, etc.)

## Option 1: Development with Docker (Recommended)

### Quick Start

```bash
# Clone repository
git clone <repository-url>
cd ace-checkin

# Copy environment file
cp .env.example .env

# Start all services (database, app, nginx)
docker-compose up

# In a new terminal, run migrations
docker-compose exec app alembic upgrade head

# Verify
curl http://localhost:8000/health
```

### Access the Application

- **API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **Database**: localhost:5432

### Useful Docker Commands

```bash
# View logs
docker-compose logs -f app

# Access database shell
docker-compose exec db psql -U ace_user -d ace_checkin

# Access application shell
docker-compose exec app bash

# Stop services
docker-compose down

# Rebuild after dependency changes
docker-compose build
docker-compose up

# Remove everything including volumes
docker-compose down -v
```

## Option 2: Local Development Without Docker

### Step 1: Set Up PostgreSQL

**On macOS (using Homebrew):**
```bash
brew install postgresql
brew services start postgresql
createdb ace_checkin
```

**On Ubuntu/Debian:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres createdb ace_checkin
```

**On Windows:**
- Download PostgreSQL installer from postgresql.org
- Run installer and create database in pgAdmin

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy example file
cp .env.example .env

# Edit .env with local settings
# For local development, use:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/ace_checkin
```

### Step 5: Run Migrations

```bash
alembic upgrade head
```

### Step 6: Start Development Server

```bash
# With auto-reload on file changes
uvicorn app.main:app --reload

# Specify host and port
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 7: Access the Application

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure and File Purposes

```
ace-checkin/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI app and endpoints
│   ├── models.py                # SQLModel database models
│   ├── schemas.py               # Pydantic request/response models
│   ├── database.py              # Database connection and sessions
│   └── config.py                # Configuration from environment
├── alembic/
│   ├── env.py                   # Alembic environment config
│   ├── script.py.mako           # Migration template
│   └── versions/                # Migration files
├── nginx/
│   ├── nginx.conf               # Main Nginx config
│   └── conf.d/default.conf      # App routing config
├── docker-compose.yml           # Docker Compose config
├── Dockerfile                   # App container definition
├── requirements.txt             # Python dependencies
└── README.md                    # Documentation
```

## Common Development Tasks

### Adding a New API Endpoint

1. **Define Schema** (if needed)
   ```python
   # In app/schemas.py
   class NewRequestSchema(BaseModel):
       field1: str
       field2: Optional[int] = None
   ```

2. **Add Endpoint**
   ```python
   # In app/main.py
   @app.post("/api/endpoint", response_model=ResponseSchema, tags=["Tag"])
   async def my_endpoint(
       request: NewRequestSchema,
       session: Session = Depends(get_session)
   ):
       """Endpoint description"""
       # Implementation
       return result
   ```

3. **Test Endpoint**
   ```bash
   curl -X POST http://localhost:8000/api/endpoint \
     -H "Content-Type: application/json" \
     -d '{"field1": "value", "field2": 123}'
   ```

### Creating a New Database Model

1. **Define Model** (in `app/models.py`)
   ```python
   class NewModel(SQLModel, table=True):
       __tablename__ = "new_table"

       id: Optional[int] = Field(default=None, primary_key=True)
       name: str = Field(sa_column=Column(String(255), nullable=False))
       created_at: datetime = Field(default_factory=datetime.utcnow)
   ```

2. **Create Migration**
   ```bash
   # Auto-detect changes
   alembic revision --autogenerate -m "Add new table"

   # Or create manually
   alembic revision -m "Add new table"
   ```

3. **Review and Run Migration**
   ```bash
   # Check the generated migration file
   cat alembic/versions/XXX_add_new_table.py

   # Apply migration
   alembic upgrade head
   ```

### Running Database Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific number of migrations
alembic upgrade +2

# Go back one version
alembic downgrade -1

# Go to specific version
alembic downgrade 001

# View migration history
alembic history

# View current revision
alembic current
```

### Database Queries During Development

```bash
# Access PostgreSQL shell locally
psql -d ace_checkin

# Or with Docker
docker-compose exec db psql -U ace_user -d ace_checkin
```

Useful SQL commands:
```sql
-- List all tables
\dt

-- Describe table structure
\d members

-- View data
SELECT * FROM members;
SELECT * FROM entry_logs ORDER BY timestamp DESC LIMIT 10;

-- Count records
SELECT COUNT(*) FROM payment_logs;

-- Exit
\q
```

## Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Create member
curl -X POST http://localhost:8000/api/members \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "TEST001",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-1234"
  }'

# Get member
curl http://localhost:8000/api/members/TEST001

# List members
curl http://localhost:8000/api/members

# Record entry (Barcode Scanner Friendly - GET)
curl "http://localhost:8000/api/entry/checkin/TEST001?notes=Court+A"

# Record entry (API - POST)
curl -X POST http://localhost:8000/api/entry \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "TEST001",
    "notes": "Court A"
  }'

# Record payment (Barcode Scanner Friendly - GET)
curl "http://localhost:8000/api/payment/checkin/TEST001?amount=25.50&notes=Monthly+fee"

# Record payment (API - POST)
curl -X POST http://localhost:8000/api/payment \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "TEST001",
    "amount": 25.50,
    "notes": "Monthly fee"
  }'

# Get payment summary
curl http://localhost:8000/api/payment/summary/TEST001
```

### Using Python

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Create member
response = requests.post(
    f"{BASE_URL}/api/members",
    json={
        "member_id": "TEST001",
        "name": "Jane Doe",
        "email": "jane@example.com"
    }
)
print(response.json())

# Record entry
response = requests.post(
    f"{BASE_URL}/api/entry",
    json={
        "member_id": "TEST001",
        "notes": "Court B"
    }
)
print(response.json())
```

### Using Swagger UI

1. Navigate to http://localhost:8000/docs
2. Click on an endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

## Code Style and Best Practices

### Python Code Style

Follow PEP 8 standards. Key points:
- 4 spaces for indentation
- 79 characters per line (100 for code)
- Type hints for all functions
- Docstrings for all public functions

```python
def create_entry(
    member_id: str,
    notes: Optional[str] = None,
    session: Session = Depends(get_session)
) -> EntryLogResponse:
    """
    Create an entry log for a member.

    Args:
        member_id: The member's ID
        notes: Optional notes for the entry
        session: Database session

    Returns:
        EntryLogResponse with created entry details
    """
    # Implementation
    pass
```

### Commit Messages

Write clear, descriptive commit messages:

```bash
# Good
git commit -m "feat: add payment summary endpoint"
git commit -m "fix: handle missing member in entry endpoint"
git commit -m "docs: update API documentation"

# Bad
git commit -m "update"
git commit -m "fix bug"
git commit -m "changes"
```

## Debugging

### Enable Debug Logging

```bash
# Set DEBUG environment variable
export DEBUG=true

# Or in .env
DEBUG=true

# Start server
uvicorn app.main:app --reload --log-level debug
```

### Using Print Statements

```python
# Add debugging in FastAPI endpoint
@app.post("/api/endpoint")
async def my_endpoint(data: MySchema):
    print(f"Received data: {data}")
    print(f"Data type: {type(data)}")
    # Rest of code
```

### Using Python Debugger

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use Python 3.7+
breakpoint()

# Then interact in terminal:
# n  - next line
# s  - step into
# c  - continue
# p  - print variable
```

### Using VS Code Debugger

Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": ["app.main:app", "--reload"],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```

Then press F5 to debug.

## Performance Testing

### Load Testing with Apache Bench

```bash
# Install
sudo apt-get install apache2-utils

# Simple load test
ab -n 100 -c 10 http://localhost:8000/health

# With authentication headers
ab -n 100 -c 10 -H "Authorization: Bearer token" http://localhost:8000/api/members
```

### Using Python Requests

```python
import time
import requests
from concurrent.futures import ThreadPoolExecutor

def make_request():
    return requests.get("http://localhost:8000/health")

# Make 100 concurrent requests
with ThreadPoolExecutor(max_workers=10) as executor:
    start = time.time()
    results = list(executor.map(lambda _: make_request(), range(100)))
    elapsed = time.time() - start

print(f"Completed {len(results)} requests in {elapsed:.2f} seconds")
print(f"Success: {sum(1 for r in results if r.status_code == 200)}")
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### Database Connection Issues

```bash
# Test connection locally
psql -d ace_checkin -c "SELECT version();"

# Check connection string
echo $DATABASE_URL

# Test with Python
python3 -c "from app.database import engine; print(engine.connect())"
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python path
python3 -c "import sys; print(sys.path)"

# Verify app structure
ls -la app/
```

### Alembic Issues

```bash
# Check migration status
alembic current

# View heads
alembic heads

# View branches
alembic branches

# Reset to initial state (development only!)
# Delete all versions, restart database
```

## Useful Development Tools

### IPython

```bash
pip install ipython

# Start interactive shell
ipython

# Query database interactively
from app.database import SessionLocal
db = SessionLocal()
db.query(Member).all()
```

### Python Linting

```bash
# Install linters
pip install pylint flake8 black

# Format code
black app/

# Check style
flake8 app/

# Lint
pylint app/
```

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
# Commit regularly
git add .
git commit -m "feat: description"

# Push to remote
git push origin feature/new-feature

# Create pull request on GitHub

# After review and merge, clean up
git checkout main
git pull
git branch -d feature/new-feature
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

Happy developing! 💻
