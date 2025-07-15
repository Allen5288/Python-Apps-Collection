from decouple import config

# Database
DATABASE_URL = config("DATABASE_URL", default="sqlite:///./test.db")

# Security
SECRET_KEY = config("SECRET_KEY", default="your-secret-key-here")
ALGORITHM = config("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)

# API
API_V1_STR = "/api/v1"
PROJECT_NAME = config("PROJECT_NAME", default="FastAPI Best Practice")

# CORS
BACKEND_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
]
