from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middlewares.exception_handlers import catch_exception_middleware
from routes.upload_pdfs import router as upload_router
from routes.ask_question import router as ask_router

app = FastAPI(
    title="Medical Assistant API",
    description="API for Medical AI Assistant",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# middleware exception handlers
app.middleware("http")(catch_exception_middleware)

# routers
# 1. upload pdf document
app.include_router(upload_router)

# 2. asking query
app.include_router(ask_router)
