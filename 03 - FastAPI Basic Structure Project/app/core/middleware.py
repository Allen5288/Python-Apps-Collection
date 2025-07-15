from fastapi import Request
from fastapi.responses import JSONResponse
import logging
import time

logger = logging.getLogger(__name__)


async def catch_exceptions_middleware(request: Request, call_next):
    """Middleware to catch unhandled exceptions"""
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred",
                "detail": str(exc) if logger.level == logging.DEBUG else None
            }
        )


async def logging_middleware(request: Request, call_next):
    """Middleware to log requests"""
    start_time = time.time()
    
    # Log request
    logger.info(f"{request.method} {request.url}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )
    
    return response
