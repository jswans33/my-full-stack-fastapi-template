"""
Example of how to use the logging utility in your code.

This file demonstrates various ways to use the logging utility
in your FastAPI application.
"""

import time

from app.core.logging import get_logger
from fastapi import APIRouter, HTTPException, Request

# Get a logger for this module
logger = get_logger(__name__)

# Create a router for this example
router = APIRouter()


@router.get("/log-example")
async def log_example():
    """Example endpoint that demonstrates different log levels."""
    # Log at different levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    # Log with additional context
    user_id = "123"
    logger.info("User logged in", extra={"user_id": user_id, "source": "example"})

    return {"message": "Logs generated, check your console or log file"}


@router.get("/log-performance")
async def log_performance():
    """Example endpoint that demonstrates performance logging."""
    # Start timing
    start_time = time.time()

    # Simulate some work
    logger.info("Starting expensive operation")
    time.sleep(1)  # Simulate work

    # Calculate duration
    duration = time.time() - start_time

    # Log performance metrics
    logger.info(
        "Expensive operation completed",
        extra={
            "duration_ms": round(duration * 1000),
            "operation": "expensive_calculation",
        },
    )

    return {
        "message": "Performance logs generated",
        "duration_ms": round(duration * 1000),
    }


@router.get("/log-exception")
async def log_exception():
    """Example endpoint that demonstrates exception logging."""
    try:
        # Simulate an error
        logger.info("Attempting division by zero")
        result = 1 / 0
        return {"result": result}
    except Exception as e:
        # Log the exception with context
        logger.exception(
            "Error occurred during calculation",
            exc_info=e,
            extra={"operation": "division"},
        )
        # Re-raise as HTTP exception
        raise HTTPException(status_code=500, detail="Calculation error")


@router.get("/log-request-context")
async def log_request_context(request: Request):
    """
    Example endpoint that demonstrates logging with request context.

    The LoggingMiddleware automatically adds request context to all logs
    within a request, but you can also access and use the request context
    directly.
    """
    # Access request ID from state (set by LoggingMiddleware)
    request_id = getattr(request.state, "request_id", "unknown")

    # Log with request context
    logger.info(
        "Processing request",
        extra={"request_id": request_id, "custom_data": "example value"},
    )

    return {"message": "Request context logged", "request_id": request_id}


# How to use the logger in your own code:
#
# 1. Import the get_logger function:
#    from app.core.logging import get_logger
#
# 2. Create a logger for your module:
#    logger = get_logger(__name__)
#
# 3. Use the logger in your code:
#    logger.info("This is an info message")
#    logger.error("This is an error message")
#
# 4. Add context to your logs:
#    logger.info("User action", extra={"user_id": user.id, "action": "login"})
#
# 5. Log exceptions:
#    try:
#        # Some code that might raise an exception
#        result = 1 / 0
#    except Exception as e:
#        logger.exception("An error occurred", exc_info=e)
