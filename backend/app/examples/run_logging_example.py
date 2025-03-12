"""
This script demonstrates the logging system in action.
Run this script directly to see the logging output.
"""

# Set up logging with DEBUG level to see all logs
import os
import time

from app.core.logging import get_logger, setup_logging

os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["LOG_FORMAT"] = (
    "JSON"  # Use JSON format to see all fields including redacted ones
)
setup_logging()

# Create a logger for this module
logger = get_logger(__name__)


def main():
    """Run logging examples."""
    logger.info("Starting logging example")

    # Basic logging at different levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    # Structured logging with extra context
    user_id = "123"
    logger.info(
        "User logged in",
        extra={"user_id": user_id, "ip_address": "192.168.1.1", "browser": "Chrome"},
    )

    # Performance logging
    logger.info("Starting expensive operation")
    start_time = time.time()

    # Simulate some work
    time.sleep(1)

    duration = time.time() - start_time
    logger.info(
        "Expensive operation completed",
        extra={"duration_ms": round(duration * 1000), "operation": "example_operation"},
    )

    # Exception logging
    try:
        logger.info("Attempting division by zero")
        result = 1 / 0
    except Exception as e:
        logger.exception(
            "Error occurred during calculation",
            exc_info=e,
            extra={"operation": "division"},
        )

    # Sensitive information handling
    logger.info(
        "Processing payment",
        extra={
            "user_id": "456",
            "amount": 100.00,
            "password": "supersecret",  # This should be redacted
            "credit_card": "4111-1111-1111-1111",  # This should be redacted
            "api_key": "sk_test_abcdefg",  # This should be redacted
        },
    )

    # Test the modules we added logging to
    logger.info("Testing modules with logging")

    # Import the modules to trigger their logging
    from datetime import timedelta

    from app.api import deps
    from app.core import security

    # Create a token to trigger security logging
    token = security.create_access_token(
        subject="test-user", expires_delta=timedelta(minutes=30)
    )

    # Try to get a database session to trigger db logging
    try:
        logger.info("Attempting to get database session")
        # This will trigger the db logging
        session_gen = deps.get_db()
        next(session_gen)
    except Exception as e:
        logger.exception(
            "Database session error (expected in this example)", exc_info=e
        )

    logger.info("Logging example completed")


if __name__ == "__main__":
    main()
