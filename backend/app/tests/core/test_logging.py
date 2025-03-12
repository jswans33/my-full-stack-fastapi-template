import io
import json
import logging

from fastapi import FastAPI
from fastapi.testclient import TestClient

# These imports will be available once we implement the logging module
# from app.core.logging import LogConfig, LoggingMiddleware, get_logger, setup_logging


class TestLogging:
    """Test suite for the logging utility."""

    def test_get_logger(self, monkeypatch):
        """Test that get_logger returns a logger with the correct name."""
        # Import here to avoid circular imports during testing
        from app.core.logging import get_logger

        logger = get_logger("test_module")
        assert logger.name == "test_module"
        assert isinstance(logger, logging.Logger)

    def test_logger_propagation(self, monkeypatch):
        """Test that loggers properly propagate to the root logger."""
        # Import here to avoid circular imports during testing
        from app.core.logging import get_logger

        logger = get_logger("test_module")
        assert logger.propagate is True

    def test_log_level_configuration(self, monkeypatch):
        """Test that log levels can be configured."""
        # Mock environment variables
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        # Import here to avoid circular imports during testing
        from app.core.logging import get_logger, setup_logging

        # Reset logging configuration
        logging.root.handlers = []

        # Setup logging with test configuration
        setup_logging()

        logger = get_logger("test_module")
        assert logger.getEffectiveLevel() == logging.DEBUG

        # Change log level and verify
        monkeypatch.setenv("LOG_LEVEL", "ERROR")
        setup_logging()
        logger = get_logger("test_module")
        assert logger.getEffectiveLevel() == logging.ERROR

    def test_log_format_text(self, monkeypatch):
        """Test that logs are formatted correctly in text format."""
        # Mock environment variables
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        monkeypatch.setenv("LOG_FORMAT", "TEXT")

        # Capture log output
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)

        # Import here to avoid circular imports during testing
        from app.core.logging import get_logger, setup_logging

        # Reset logging configuration
        logging.root.handlers = []

        # Setup logging with test configuration and test handler
        setup_logging(test_handler=handler)

        # Log a test message
        logger = get_logger("test_module")
        logger.info("Test message")

        # Verify log format
        log_output = log_stream.getvalue()
        assert "INFO" in log_output
        assert "test_module" in log_output
        assert "Test message" in log_output

    def test_log_format_json(self, monkeypatch):
        """Test that logs are formatted correctly in JSON format."""
        # Mock environment variables
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        monkeypatch.setenv("LOG_FORMAT", "JSON")

        # Capture log output
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)

        # Import here to avoid circular imports during testing
        from app.core.logging import get_logger, setup_logging

        # Reset logging configuration
        logging.root.handlers = []

        # Setup logging with test configuration and test handler
        setup_logging(test_handler=handler)

        # Log a test message
        logger = get_logger("test_module")
        logger.info("Test message")

        # Verify JSON format
        log_output = log_stream.getvalue()
        log_data = json.loads(log_output)
        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test_module"
        assert log_data["message"] == "Test message"

    def test_structured_logging(self, monkeypatch):
        """Test that structured logging works correctly."""
        # Mock environment variables
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        monkeypatch.setenv("LOG_FORMAT", "JSON")

        # Capture log output
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)

        # Import here to avoid circular imports during testing
        from app.core.logging import get_logger, setup_logging

        # Reset logging configuration
        logging.root.handlers = []

        # Setup logging with test configuration and test handler
        setup_logging(test_handler=handler)

        # Log a test message with extra context
        logger = get_logger("test_module")
        logger.info(
            "User logged in", extra={"user_id": "123", "email": "test@example.com"}
        )

        # Verify structured logging
        log_output = log_stream.getvalue()
        log_data = json.loads(log_output)
        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test_module"
        assert log_data["message"] == "User logged in"
        assert log_data["user_id"] == "123"
        assert log_data["email"] == "test@example.com"

    def test_logging_middleware(self, monkeypatch):
        """Test that the logging middleware captures request information."""
        # Mock environment variables
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        monkeypatch.setenv("LOG_FORMAT", "JSON")

        # Import here to avoid circular imports during testing
        from app.core.logging import LoggingMiddleware, get_logger, setup_logging

        # Create a test FastAPI app
        app = FastAPI()

        # Add the logging middleware
        app.add_middleware(LoggingMiddleware)

        # Add a test endpoint
        @app.get("/test")
        async def test_endpoint():
            logger = get_logger("test_endpoint")
            logger.info("Test endpoint called")
            return {"message": "Test endpoint"}

        # Capture log output
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)

        # Reset logging configuration
        logging.root.handlers = []

        # Setup logging with test configuration and test handler
        setup_logging(test_handler=handler)

        # Create a test client
        client = TestClient(app)

        # Make a test request
        response = client.get("/test", headers={"X-Request-ID": "test-request-id"})

        # Verify response
        assert response.status_code == 200

        # Verify log output
        log_output = log_stream.getvalue()
        log_lines = log_output.strip().split("\n")
        assert len(log_lines) >= 1

        # Find the log lines for request information and endpoint call
        request_log = None
        endpoint_log = None

        for line in log_lines:
            try:
                log_data = json.loads(line)
                message = log_data.get("message", "")
                if "Request started:" in message:
                    request_log = log_data
                elif message == "Test endpoint called":
                    endpoint_log = log_data
            except json.JSONDecodeError:
                continue

        # Assert that we found both logs
        assert request_log is not None, "Could not find request log"
        assert endpoint_log is not None, (
            "Could not find log with 'Test endpoint called' message"
        )

        # Verify request log has the expected context
        assert request_log["request_id"] == "test-request-id"
        assert request_log["path"] == "/test"
        assert request_log["method"] == "GET"

        # Verify endpoint log has the expected message
        assert endpoint_log["message"] == "Test endpoint called"
        assert endpoint_log["logger"] == "test_endpoint"

    def test_exception_logging(self, monkeypatch):
        """Test that exceptions are logged correctly."""
        # Mock environment variables
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        monkeypatch.setenv("LOG_FORMAT", "JSON")

        # Capture log output
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)

        # Import here to avoid circular imports during testing
        from app.core.logging import get_logger, setup_logging

        # Reset logging configuration
        logging.root.handlers = []

        # Setup logging with test configuration and test handler
        setup_logging(test_handler=handler)

        # Log an exception
        logger = get_logger("test_module")
        try:
            1 / 0
        except Exception as e:
            logger.exception("An error occurred", exc_info=e)

        # Verify exception logging
        log_output = log_stream.getvalue()
        log_data = json.loads(log_output)
        assert log_data["level"] == "ERROR"
        assert log_data["logger"] == "test_module"
        assert log_data["message"] == "An error occurred"
        assert "exc_info" in log_data
        assert "ZeroDivisionError" in log_data["exc_info"]
