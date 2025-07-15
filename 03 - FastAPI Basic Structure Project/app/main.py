from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from .config import PROJECT_NAME, BACKEND_CORS_ORIGINS, API_V1_STR
from .core.exceptions import CustomException
from .api.v1.api import api_router

# Create FastAPI instance
app = FastAPI(
    title=PROJECT_NAME,
    openapi_url=f"{API_V1_STR}/openapi.json",
    description="FastAPI application following best practices",
    version="1.0.0"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Custom exception handler
@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error_type, "message": exc.message, "detail": exc.detail}
    )


# Include API router
app.include_router(api_router, prefix=API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "FastAPI Best Practice Application"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}


if __name__ == "__main__":
    import uvicorn
    # Use port 8080 as default to avoid Windows port 8000 issues
    uvicorn.run(app, host="0.0.0.0", port=8080)
