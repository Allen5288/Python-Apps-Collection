# FastAPI Best Practice Project Structure

This project demonstrates a production-ready FastAPI application structure following best practices.

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database connection and session
│   ├── dependencies.py        # Dependency injection
│   ├── models/                # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── user.py
│   ├── schemas/               # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── user.py
│   ├── api/                   # API routes
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── users.py
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── user_service.py
│   ├── core/                  # Core functionality
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   ├── middleware.py
│   │   └── security.py
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_users.py
├── alembic/                   # Database migrations
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Features

- **CRUD Operations**: Complete Create, Read, Update, Delete operations
- **Data Models**: SQLAlchemy ORM models with relationships
- **Pydantic Schemas**: Request/response validation and serialization
- **API Routes**: RESTful API endpoints with proper HTTP methods
- **Services**: Business logic separation from API handlers
- **Error Handling**: Custom exception handling and middleware
- **Authentication**: JWT-based authentication system
- **Testing**: Comprehensive test suite with pytest
- **Database**: PostgreSQL with Alembic migrations
- **Docker**: Containerized application with docker-compose

## Setup

1. **Clone and install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run with Docker:**
   ```bash
   docker-compose up --build
   ```

4. **Or run locally:**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
pytest tests/
```

## Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```
