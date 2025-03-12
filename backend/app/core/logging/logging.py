import json
import logging
import sys
from datetime import datetime, timezone
from enum import Enum
from logging.handlers import RotatingFileHandler

from app.core.config import settings
from fastapi import Request
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


# Define log levels
class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Define log formats
class LogFormat(str, Enum):
    TEXT = "TEXT"
    JSON = "JSON"


# Configuration model for logging
class LogConfig(BaseModel):
    """Configuration for the logging system."""

    level: LogLevel = Field(
        default=LogLevel.INFO, description="Minimum log level to record"
    )
    format: LogFormat = Field(
        default=LogFormat.TEXT, description="Format for log output (TEXT or JSON)"
    )
    file: str | None = Field(
        default=None, description="Path to log file (if file logging is enabled)"
    )
    rotation: bool = Field(default=False, description="Enable log rotation")
    rotation_size: int = Field(
        default=10, description="Maximum size of log file before rotation (in MB)"
    )
    rotation_backups: int = Field(
        default=5, description="Number of backup files to keep"
    )

    @classmethod
    def from_env(cls) -> "LogConfig":
        """Create a LogConfig from environment variables or settings."""
        import os

        # Get log level from environment or settings
        level_str = os.getenv("LOG_LEVEL")
        if level_str is None and hasattr(settings, "LOG_LEVEL"):
            level_str = settings.LOG_LEVEL
        if not level_str:
            level_str = "INFO"

        try:
            level = LogLevel(level_str)
        except ValueError:
            level = LogLevel.INFO

        # Get log format from environment or settings
        format_str = os.getenv("LOG_FORMAT")
        if format_str is None and hasattr(settings, "LOG_FORMAT"):
            format_str = settings.LOG_FORMAT
        if not format_str:
            format_str = "TEXT"

        try:
            log_format = LogFormat(format_str)
        except ValueError:
            log_format = LogFormat.TEXT

        # Get other settings from environment or settings
        log_file = os.getenv("LOG_FILE")
        if log_file is None and hasattr(settings, "LOG_FILE"):
            log_file = settings.LOG_FILE

        log_rotation_str = os.getenv("LOG_ROTATION")
        if log_rotation_str is None and hasattr(settings, "LOG_ROTATION"):
            log_rotation = settings.LOG_ROTATION
        else:
            log_rotation = log_rotation_str == "True" if log_rotation_str else False

        log_rotation_size_str = os.getenv("LOG_ROTATION_SIZE")
        if log_rotation_size_str is None and hasattr(settings, "LOG_ROTATION_SIZE"):
            log_rotation_size = settings.LOG_ROTATION_SIZE
        else:
            log_rotation_size = (
                int(log_rotation_size_str) if log_rotation_size_str else 10
            )

        log_rotation_backups_str = os.getenv("LOG_ROTATION_BACKUPS")
        if log_rotation_backups_str is None and hasattr(
            settings, "LOG_ROTATION_BACKUPS"
        ):
            log_rotation_backups = settings.LOG_ROTATION_BACKUPS
        else:
            log_rotation_backups = (
                int(log_rotation_backups_str) if log_rotation_backups_str else 5
            )

        return cls(
            level=level,
            format=log_format,
            file=log_file,
            rotation=log_rotation,
            rotation_size=log_rotation_size,
            rotation_backups=log_rotation_backups,
        )


# Context variables for request tracking
_request_id_var = "request_id"
_request_method_var = "method"
_request_path_var = "path"
_request_ip_var = "ip"
_request_user_agent_var = "user_agent"
_request_user_id_var = "user_id"


# Define sensitive fields that should be redacted from logs
SENSITIVE_FIELDS = {"password", "secret", "token", "api_key", "auth", "credential"}

# Maximum message length to prevent overly large log entries
MAX_MESSAGE_LENGTH = 5000  # 5KB


# Custom JSON formatter
class JsonFormatter(logging.Formatter):
    """Format logs as JSON for better parsing."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON."""
        # Truncate message if it's too long
        message = record.getMessage()
        if len(message) > MAX_MESSAGE_LENGTH:
            message = message[:MAX_MESSAGE_LENGTH] + "... [truncated]"

        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": message,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if available
        if record.exc_info:
            log_data["exc_info"] = self.formatException(record.exc_info)

        # Add extra fields from the record
        if hasattr(record, "__dict__"):
            for key, value in record.__dict__.items():
                if key not in {
                    "args",
                    "asctime",
                    "created",
                    "exc_info",
                    "exc_text",
                    "filename",
                    "funcName",
                    "id",
                    "levelname",
                    "levelno",
                    "lineno",
                    "module",
                    "msecs",
                    "message",
                    "msg",
                    "name",
                    "pathname",
                    "process",
                    "processName",
                    "relativeCreated",
                    "stack_info",
                    "thread",
                    "threadName",
                }:
                    # Check if this is a sensitive field that should be redacted
                    if any(sensitive in key.lower() for sensitive in SENSITIVE_FIELDS):
                        log_data[key] = "[REDACTED]"
                    else:
                        # Ensure the value is serializable
                        try:
                            # Test if the value is JSON serializable
                            json.dumps({key: value})
                            log_data[key] = value
                        except (TypeError, OverflowError):
                            # If not serializable, convert to string
                            log_data[key] = str(value)

        # Ensure we return a valid JSON string
        try:
            return json.dumps(log_data)
        except Exception as e:
            # Fallback to a simple JSON if serialization fails
            return json.dumps(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": "ERROR",
                    "logger": "json_formatter",
                    "message": f"Failed to serialize log: {str(e)}",
                    "original_message": record.getMessage(),
                }
            )


def setup_logging(
    config: LogConfig | None = None, test_handler: logging.Handler | None = None
) -> None:
    """Set up logging based on configuration."""
    if config is None:
        config = LogConfig.from_env()

    # Get the root logger
    root_logger = logging.getLogger()

    # Set the log level using the enum value directly
    log_level = getattr(logging, config.level)
    root_logger.setLevel(log_level)

    # Also set the level for all existing loggers to ensure consistency
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)

    # Clear all existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatter based on format type
    if config.format == LogFormat.JSON:
        formatter: logging.Formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # If a test handler is provided, use it
    if test_handler:
        test_handler.setFormatter(formatter)
        root_logger.addHandler(test_handler)
    else:
        # Add console handler by default
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # Add file handler if configured
        if config.file:
            if config.rotation:
                rotating_handler = RotatingFileHandler(
                    config.file,
                    maxBytes=config.rotation_size * 1024 * 1024,
                    backupCount=config.rotation_backups,
                )
                rotating_handler.setFormatter(formatter)
                root_logger.addHandler(rotating_handler)
            else:
                file_handler = logging.FileHandler(config.file)
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)

    # Configure Sentry integration if available and configured
    try:
        if (
            hasattr(settings, "SENTRY_DSN")
            and settings.SENTRY_DSN
            and settings.ENVIRONMENT != "local"
        ):
            try:
                import sentry_sdk
                from sentry_sdk.integrations.logging import LoggingIntegration

                # Configure Sentry to capture errors and above
                sentry_logging = LoggingIntegration(
                    level=logging.ERROR, event_level=logging.ERROR
                )

                sentry_sdk.init(
                    dsn=str(settings.SENTRY_DSN),
                    integrations=[sentry_logging],
                    environment=settings.ENVIRONMENT,
                    traces_sample_rate=1.0,
                )

                logging.getLogger("app").info("Sentry integration enabled")
            except ImportError:
                logging.getLogger("app").warning(
                    "Sentry SDK not installed, skipping integration"
                )
    except (AttributeError, TypeError):
        # Sentry is not configured, skip integration
        pass


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    logger = logging.getLogger(name)

    # Ensure the logger inherits the root logger's level
    if logger.level == logging.NOTSET:
        root_level = logging.getLogger().level
        logger.setLevel(root_level)

    return logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to add request context to logs."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request and add context to logs."""
        # Extract request information
        request_id = request.headers.get("X-Request-ID", "")
        if not request_id:
            # Generate a request ID if not provided
            import uuid

            request_id = str(uuid.uuid4())

        # Add request ID header to the request state for later use
        request.state.request_id = request_id

        # Create a context dict for logging
        context = {
            _request_id_var: request_id,
            _request_method_var: request.method,
            _request_path_var: request.url.path,
            _request_ip_var: request.client.host if request.client else "",
            _request_user_agent_var: request.headers.get("User-Agent", ""),
        }

        # Add user ID if available (requires authentication)
        if hasattr(request.state, "user") and hasattr(request.state.user, "id"):
            context[_request_user_id_var] = request.state.user.id

        # Create a logger for this request
        logger = get_logger("app.request")

        # Log the request
        logger.info(
            f"Request started: {request.method} {request.url.path}", extra=context
        )

        # Process the request and measure timing
        import time

        start_time = time.time()

        try:
            response = await call_next(request)

            # Calculate request duration
            duration = time.time() - start_time

            # Log the response
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"- Status: {response.status_code} - Duration: {duration:.3f}s",
                extra=context,
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response
        except Exception as e:
            # Calculate request duration
            duration = time.time() - start_time

            # Log the exception
            logger.exception(
                f"Request failed: {request.method} {request.url.path} "
                f"- Duration: {duration:.3f}s - Error: {str(e)}",
                exc_info=e,
                extra=context,
            )

            # Re-raise the exception
            raise


# Initialize logging when the module is imported
setup_logging()
