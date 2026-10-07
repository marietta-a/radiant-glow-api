import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from app.config import logger


async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler for the entire application.
    """
    # Log the full traceback for the server logs
    logger.error(f"Global Exception Caught: {str(exc)}")
    logger.error(traceback.format_exc())

    # Determine status code based on exception type
    status_code = 500
    error_message = "An unexpected error occurred during clinical analysis."
    error_type = type(exc).__name__

    # Customize messages for specific errors
    if "API_KEY" in str(exc):
        status_code = 401
        error_message = "Authentication error: AI services are not properly configured."
    elif "429" in str(exc) or "quota" in str(exc).lower():
        status_code = 429
        error_message = "Usage limit exceeded. Please try again later."
    elif "Precision mismatch" in str(exc):
        status_code = 422
        error_message = str(exc)

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "type": error_type,
                "message": error_message,
                "suggestion": "Ensure the image is well-lit and contains food items."
            }
        }
    )