# FastAPI Best Practice Project Structure

This project demonstrates a production-ready FastAPI application structure following industry best practices and modern development patterns. It provides a comprehensive foundation for building scalable, maintainable, and secure web APIs with FastAPI.

The project implements a clean architecture with clear separation of concerns, making it easy to understand, test, and extend. It includes authentication, database operations, error handling, testing, and deployment configurations.

## Project Structure

```text
.
├── app/                       # Main application package
│   ├── __init__.py
│   ├── main.py                # FastAPI application entry point
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
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   └── test_users.py
├── alembic/                   # Database migrations
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── Dockerfile                 # Docker container configuration
├── docker-compose.yml         # Multi-service Docker setup
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## Detailed Component Overview

### 🚀 Application Core (`app/`)

#### **Main Application (`main.py`)**
The entry point of the FastAPI application that:
- Initializes the FastAPI instance with metadata and configuration
- Sets up CORS middleware for cross-origin requests
- Configures global exception handlers for consistent error responses
- Includes API routers with proper versioning
- Provides health check endpoints for monitoring

#### **Configuration Management (`config.py`)**
Centralized configuration handling that:
- Manages environment variables with sensible defaults
- Provides database connection strings
- Handles JWT authentication settings
- Configures API versioning and CORS origins
- Uses python-decouple for environment variable management

#### **Database Layer (`database.py`)**
Database connectivity and session management:
- SQLAlchemy engine configuration with connection pooling
- Session factory for database operations
- Dependency injection for database sessions
- Base model class for all database entities

### 📊 Data Layer

#### **Models (`models/`)**
SQLAlchemy ORM models that:
- **`base.py`**: Provides common fields (id, timestamps) for all models
- **`user.py`**: User entity with authentication fields and relationships
- Include proper indexing for performance
- Define table relationships and constraints
- Support for soft deletes and audit trails

#### **Schemas (`schemas/`)**
Pydantic models for data validation and serialization:
- **Request validation**: Ensure incoming data meets requirements
- **Response serialization**: Control what data is returned to clients
- **Custom validators**: Email format, password strength, username rules
- **Type safety**: Full type hints for better IDE support and error catching

### 🌐 API Layer (`api/`)

#### **Routing Structure (`api/v1/`)**
Well-organized API endpoints with:
- **Version management**: `/api/v1/` prefix for API evolution
- **Resource-based routing**: RESTful endpoint organization
- **Dependency injection**: Shared dependencies across endpoints
- **Authentication integration**: Protected and public endpoints

#### **User Endpoints (`endpoints/users.py`)**
Comprehensive user management API:
- **Authentication**: Registration, login with JWT tokens
- **CRUD operations**: Create, read, update, soft delete users
- **Pagination**: Efficient data retrieval with skip/limit
- **Authorization**: Role-based access control (admin vs user)
- **Input validation**: Comprehensive request validation

### 🧠 Business Logic (`services/`)

#### **Service Layer Architecture**
Clean separation of business logic from API handlers:
- **Base service**: Generic CRUD operations for any model
- **User service**: Specialized user operations with business rules
- **Transaction management**: Proper database transaction handling
- **Error handling**: Business rule validation and custom exceptions

### 🔧 Core Functionality (`core/`)

#### **Security (`security.py`)**
Robust authentication and authorization:
- **Password hashing**: bcrypt for secure password storage
- **JWT tokens**: Stateless authentication with configurable expiration
- **Token validation**: Secure token verification and user extraction

#### **Exception Handling (`exceptions.py`)**
Structured error management:
- **Custom exceptions**: Domain-specific error types
- **HTTP status mapping**: Proper HTTP responses for different errors
- **Error serialization**: Consistent error response format
- **Logging integration**: Error tracking for debugging

#### **Middleware (`middleware.py`)**
Request/response processing:
- **Request logging**: Track API usage and performance
- **Error catching**: Global exception handling
- **Performance monitoring**: Request timing and metrics

### 🛠 Utilities (`utils/`)

#### **Helper Functions (`helpers.py`)**
Common utility functions:
- **Data validation**: Email, password strength validation
- **String processing**: Slug generation, sanitization
- **Date/time handling**: UTC datetime utilities
- **Pagination helpers**: Query pagination utilities

### 🧪 Testing (`tests/`)

#### **Comprehensive Test Suite**
Production-ready testing framework:
- **Unit tests**: Individual component testing
- **Integration tests**: API endpoint testing
- **Test fixtures**: Reusable test data and setup
- **Database isolation**: Clean test environment for each test
- **Authentication testing**: Token-based test scenarios

### 🐳 Deployment & Infrastructure

#### **Docker Configuration**
Container-ready deployment:
- **Multi-stage builds**: Optimized production images
- **Security**: Non-root user, minimal attack surface
- **Environment configuration**: Flexible deployment settings

#### **Database Migrations (`alembic/`)**
Version-controlled database changes:
- **Schema evolution**: Safe database updates
- **Rollback support**: Ability to revert changes
- **Team collaboration**: Shared database state management

## Key Features & Capabilities

### 🔐 **Authentication & Security**
- **JWT Token Authentication**: Stateless authentication with configurable token expiration
- **Password Security**: bcrypt hashing for secure password storage
- **Role-Based Access Control**: Admin and user roles with permission-based endpoints
- **Input Validation**: Comprehensive request validation with Pydantic schemas
- **CORS Configuration**: Secure cross-origin resource sharing setup

### 📊 **CRUD Operations**
- **Complete CRUD**: Full Create, Read, Update, Delete operations for all entities
- **Soft Deletes**: User deactivation instead of hard deletion for data integrity
- **Pagination**: Efficient data retrieval with configurable page sizes
- **Filtering & Sorting**: Advanced query capabilities for large datasets
- **Bulk Operations**: Support for batch operations where applicable

### 🏗️ **Architecture & Design**
- **Clean Architecture**: Clear separation of concerns with layered design
- **Service Layer**: Business logic isolation from API controllers
- **Repository Pattern**: Generic CRUD base classes for consistent data operations
- **Dependency Injection**: FastAPI's dependency system for clean code organization
- **API Versioning**: URL-based versioning (`/api/v1/`) for backward compatibility

### 🔧 **Data Management**
- **SQLAlchemy ORM**: Type-safe database operations with relationship mapping
- **Pydantic Schemas**: Request/response validation and automatic API documentation
- **Database Migrations**: Alembic for version-controlled schema changes
- **Connection Pooling**: Optimized database connections for better performance
- **Transaction Management**: Proper ACID compliance and rollback support

### 🧪 **Testing & Quality**
- **Comprehensive Test Suite**: Unit and integration tests with pytest
- **Test Isolation**: Clean database state for each test
- **Mock Authentication**: Test fixtures for authenticated endpoints
- **Coverage Reports**: Code coverage tracking for test completeness
- **Automated Testing**: CI/CD ready test configuration

### 🐳 **DevOps & Deployment**
- **Docker Support**: Multi-stage Dockerfile for production deployments
- **Docker Compose**: Local development environment with PostgreSQL and Redis
- **Environment Configuration**: Flexible settings for different deployment stages
- **Health Checks**: Application and database health monitoring endpoints
- **Logging**: Structured logging for debugging and monitoring

### 📈 **Performance & Monitoring**
- **Async Support**: Asynchronous request handling for better performance
- **Request Logging**: Detailed request/response logging with timing
- **Error Tracking**: Comprehensive error handling and reporting
- **Middleware**: Custom middleware for cross-cutting concerns
- **Response Caching**: Redis integration for caching strategies

## Setup & Installation

### Prerequisites

Before starting, ensure you have the following installed:
- **Python 3.8+** (recommended: Python 3.11+)
- **pip** (Python package manager)
- **Git** (for version control)
- **Docker & Docker Compose** (optional, for containerized setup)
- **PostgreSQL** (optional, for local database setup)

### Environment Setup

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd fastapi-best-practice
   ```

2. **Create and activate virtual environment:**

   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows Command Prompt:
   venv\Scripts\activate
   
   # On Windows PowerShell:
   venv\Scripts\Activate.ps1
   
   # On Windows Git Bash / WSL / Linux / macOS:
   source venv/Scripts/activate
   
   # Alternative for Git Bash on Windows:
   . venv/Scripts/activate
   ```

   **Note for Windows users:** If you're using Git Bash, use `source venv/Scripts/activate` or `. venv/Scripts/activate`

3. **Install dependencies:**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Environment Variables Setup:**

   ```bash
   # Copy environment template
   cp .env.example .env
   ```

   Edit the `.env` file with your configuration:

   ```env
   # Database Configuration
   DATABASE_URL=postgresql://username:password@localhost:5432/fastapi_db
   # For development with SQLite (simpler setup):
   # DATABASE_URL=sqlite:///./fastapi_dev.db
   
   # Security Settings
   SECRET_KEY=your-super-secret-key-change-this-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # Database Credentials (for Docker)
   POSTGRES_USER=fastapi_user
   POSTGRES_PASSWORD=fastapi_password
   POSTGRES_DB=fastapi_db
   
   # Application Settings
   PROJECT_NAME="FastAPI Best Practice"
   DEBUG=True
   ```

### Database Setup

#### Option 1: Using Docker (Recommended)

```bash
# Start PostgreSQL with Docker Compose
docker-compose up -d db

# Wait for database to be ready, then run migrations
alembic upgrade head
```

#### Option 2: Local PostgreSQL Installation

```bash
# Install PostgreSQL (varies by OS)
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS with Homebrew:
brew install postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE fastapi_db;
CREATE USER fastapi_user WITH PASSWORD 'fastapi_password';
GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi_user;
\q

# Run database migrations
alembic upgrade head
```

#### Option 3: SQLite (Development Only)

```bash
# Update .env file to use SQLite
echo "DATABASE_URL=sqlite:///./fastapi_dev.db" > .env

# Run migrations
alembic upgrade head
```

### Running the Application

#### Development Server

```bash
# Start the development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# If port 8000 is busy, use an alternative port
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 3000

# Or use the development script
python setup.py dev
# Windows: dev.bat dev
# Unix/Linux: ./dev.sh dev

# For Windows Git Bash users specifically:
# If you get permission errors, try running with a different port
uvicorn app.main:app --reload --port 8080
```

#### Docker Deployment

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f web
```

#### Production Deployment

```bash
# Build production image
docker build -t fastapi-app .

# Run with production settings
docker run -p 8000:8000 --env-file .env fastapi-app
```

## API Documentation & Testing

### Interactive Documentation

Once the application is running, you can access the interactive API documentation:

- **Swagger UI**: <http://localhost:8000/docs> - Interactive API explorer with request/response examples
- **ReDoc**: <http://localhost:8000/redoc> - Alternative documentation interface with better organization

### API Testing

```bash
# Run the complete test suite
pytest tests/ -v

# Run tests with coverage report
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_users.py -v

# Run tests in parallel (faster execution)
pytest tests/ -n auto
```

### Manual API Testing

```bash
# Health check
curl http://localhost:8000/health

# Register a new user
curl -X POST "http://localhost:8000/api/v1/users/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "username": "testuser",
       "password": "securepass123",
       "full_name": "Test User"
     }'

# Login to get JWT token
curl -X POST "http://localhost:8000/api/v1/users/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=test@example.com&password=securepass123"

# Use the token for authenticated requests
curl -X GET "http://localhost:8000/api/v1/users/me" \
     -H "Authorization: Bearer <your-jwt-token>"
```

## Database Migrations

### Alembic Migration Management

```bash
# Generate a new migration after model changes
alembic revision --autogenerate -m "Add new field to user model"

# Apply all pending migrations
alembic upgrade head

# Downgrade to a specific revision
alembic downgrade <revision_id>

# Show current migration status
alembic current

# Show migration history
alembic history
```

### Migration Best Practices

- Always review auto-generated migrations before applying
- Test migrations on a copy of production data
- Create backup before running migrations in production
- Use descriptive migration messages

## Development Workflow

### Code Quality Tools

```bash
# Format code with black
black app/ tests/

# Sort imports
isort app/ tests/

# Lint with flake8
flake8 app/ tests/

# Type checking with mypy
mypy app/
```

### Git Hooks (Optional)

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Deployment

### Production Environment Variables

```env
# Production settings
DEBUG=False
DATABASE_URL=postgresql://user:pass@db-server:5432/prod_db
SECRET_KEY=super-secure-production-key
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Performance settings
UVICORN_WORKERS=4
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000
```

### Docker Production Setup

```bash
# Build production image
docker build -t fastapi-app:latest .

# Run with docker-compose in production
docker-compose -f docker-compose.prod.yml up -d

# Scale the application
docker-compose up --scale web=3
```

### Health Monitoring

```bash
# Application health check
curl http://localhost:8000/health

# Database connectivity check
curl http://localhost:8000/health/db

# Detailed system status
curl http://localhost:8000/health/detailed
```

## Security Considerations

### Production Security Checklist

- [ ] Use strong, unique SECRET_KEY in production
- [ ] Enable HTTPS with proper SSL certificates
- [ ] Configure CORS origins appropriately
- [ ] Implement rate limiting for API endpoints
- [ ] Use environment variables for all sensitive data
- [ ] Regularly update dependencies for security patches
- [ ] Implement proper logging and monitoring
- [ ] Use secure database credentials
- [ ] Enable database SSL connections
- [ ] Implement API key authentication for sensitive operations

### Security Features Included

- Password hashing with bcrypt (secure against rainbow table attacks)
- JWT tokens with configurable expiration
- Input validation and sanitization
- SQL injection prevention through ORM
- CORS configuration for cross-origin security
- Custom exception handling to prevent information leakage

## Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest tests/`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Maintain test coverage above 90%
- Use meaningful variable and function names

## Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check if PostgreSQL is running
docker-compose ps

# View database logs
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up -d db
alembic upgrade head
```

#### Permission Errors
```bash
# Fix file permissions (Unix/Linux)
chmod +x dev.sh
chmod +x setup.py

# Windows PowerShell execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Import Errors
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Port Access/Permission Errors (Windows)
```bash
# Error: [WinError 10013] An attempt was made to access a socket...
# This usually means port 8000 is already in use or blocked

# Solution 1: Use a different port
uvicorn app.main:app --reload --port 8080

# Solution 2: Check what's using port 8000
netstat -ano | findstr :8000

# Solution 3: Kill process using the port (replace PID with actual process ID)
taskkill /PID <process_id> /F

# Solution 4: Run as administrator (if needed)
# Right-click your terminal and "Run as administrator"

# Solution 5: Check Windows Defender/Firewall
# Temporarily disable Windows Defender Firewall or add Python to exceptions
```

#### Virtual Environment Issues
```bash
# If virtual environment is not working properly on Windows
# Deactivate and recreate
deactivate
rm -rf venv  # or rmdir /s venv on Windows CMD
python -m venv venv
source venv/Scripts/activate  # Git Bash
pip install -r requirements.txt
```

## Performance Optimization

### Database Optimization
- Use database indexes for frequently queried fields
- Implement connection pooling
- Use database-specific optimizations (EXPLAIN ANALYZE for PostgreSQL)
- Consider read replicas for read-heavy workloads

### Application Optimization
- Enable response compression
- Implement caching strategies with Redis
- Use async/await for I/O operations
- Profile and optimize slow endpoints

### Monitoring
- Set up application performance monitoring (APM)
- Monitor database query performance
- Track API response times
- Implement health checks and alerts

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support:
- Create an issue in the GitHub repository
- Check the API documentation at `/docs`
- Review the troubleshooting section above

---

**Happy coding! 🚀**
