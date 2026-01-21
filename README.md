# Ace Check-in

Tennis club member check-in and payment tracking system.

## Project Structure

```
ace-checkin/
├── server/          # FastAPI backend
│   ├── app/         # Application code
│   ├── alembic/     # Database migrations
│   ├── nginx/       # Nginx configuration
│   └── ...
├── mobile-client/   # React Native (Expo) mobile app
└── README.md
```

## Components

### Server (Backend)

FastAPI-based REST API for member management, entry logging, and payment tracking.

**Tech Stack:**
- Python 3.11+
- FastAPI
- SQLModel (SQLAlchemy + Pydantic)
- PostgreSQL
- Alembic (migrations)
- Docker

📖 See [`server/README.md`](server/README.md) for backend documentation.

### Mobile Client

React Native mobile app with Expo for scanning member barcodes and logging entries/payments.

**Tech Stack:**
- React Native
- Expo
- TypeScript

📖 See [`mobile-client/README.md`](mobile-client/README.md) for mobile app documentation.

## Quick Start

### Backend

```bash
cd server
docker-compose up
```

API available at: http://localhost:8000

### Mobile App

```bash
cd mobile-client
npm install
npx expo start
```

## Development

### Pre-commit Hooks

This project uses pre-commit for code quality:

```bash
# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## License

MIT License - see [LICENSE](LICENSE)
