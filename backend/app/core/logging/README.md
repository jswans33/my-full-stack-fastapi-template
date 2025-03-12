# Logging Utility

## Overview

This feature branch adds a centralized logging utility to the FastAPI backend application. The logging utility provides a consistent way to log messages throughout the application, with configurable log levels, formats, and output destinations.

## Features

- Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Structured logging with JSON format option for better parsing
- Customizable log formatting
- Log rotation to prevent log files from growing too large
- Context-based logging to track request information
- Performance metrics logging
- Optional Sentry integration for error tracking in production

## Configuration

Logging configuration is managed through environment variables or settings in the `.env` file:

- `LOG_LEVEL`: Sets the minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FORMAT`: Sets the log format (TEXT, JSON)
- `LOG_FILE`: Path to the log file (if file logging is enabled)
- `LOG_ROTATION`: Enable log rotation (True/False)
- `LOG_ROTATION_SIZE`: Maximum size of log file before rotation (in MB)
- `LOG_ROTATION_BACKUPS`: Number of backup files to keep

## Usage

### Basic Usage

```python
from app.core.logging import get_logger

# Get a logger for the current module
logger = get_logger(__name__)

# Log messages at different levels
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error message")
```

### Structured Logging

```python
# Log with additional context
logger.info("User logged in", extra={"user_id": user.id, "email": user.email})

# Log exceptions
try:
    # Some code that might raise an exception
    result = 1 / 0
except Exception as e:
    logger.exception("An error occurred during calculation", exc_info=e)
```

### Request Context Logging

The logging utility automatically captures request context when used with the FastAPI middleware:

```
# This is automatically added to all logs within a request context
# - request_id: Unique ID for the request
# - method: HTTP method (GET, POST, etc.)
# - path: Request path
# - ip: Client IP address
# - user_agent: Client user agent
# - user_id: User ID (if authenticated)
```

## Implementation Details

The logging utility is implemented in `app.core.logging` and consists of:

1. `LogConfig`: Pydantic model for logging configuration
2. `setup_logging()`: Function to set up logging based on configuration
3. `get_logger()`: Function to get a logger for a specific module
4. `LoggingMiddleware`: FastAPI middleware for request context logging

## Examples

See `backend/app/examples/logging_example.py` for examples of how to use the logging utility in your code.

## Testing

The logging utility includes comprehensive tests to ensure it works as expected. Tests are located in `app/tests/core/test_logging.py`.

## Best Practices

1. **Use the module name as the logger name**: This helps identify where logs are coming from.

   ```python
   logger = get_logger(__name__)
   ```

2. **Use appropriate log levels**:
   - DEBUG: Detailed information, typically of interest only when diagnosing problems
   - INFO: Confirmation that things are working as expected
   - WARNING: An indication that something unexpected happened, or may happen in the near future
   - ERROR: Due to a more serious problem, the software has not been able to perform some function
   - CRITICAL: A serious error, indicating that the program itself may be unable to continue running

3. **Add context to logs**: Use the `extra` parameter to add context to your logs.

   ```python
   logger.info("User action", extra={"user_id": user.id, "action": "login"})
   ```

4. **Log exceptions properly**: Use the `exception` method to log exceptions with traceback.

   ```python
   try:
       # Some code that might raise an exception
       result = 1 / 0
   except Exception as e:
       logger.exception("An error occurred", exc_info=e)
   ```

5. **Don't log sensitive information**: Be careful not to log sensitive information like passwords, tokens, or personal data.
