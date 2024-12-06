import logging
import os
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from core.config_logging import configure_logging


@pytest.fixture
def clean_logs_dir():
    """
    Fixture to clean up the logs directory before and after the test.
    """
    if os.path.exists("logs"):
        for file in os.listdir("logs"):
            os.remove(os.path.join("logs", file))
    yield
    if os.path.exists("logs"):
        for file in os.listdir("logs"):
            os.remove(os.path.join("logs", file))
        os.rmdir("logs")


def test_configure_logging_creates_logs_directory(clean_logs_dir):
    """
    Test that the `configure_logging` function creates a `logs` directory.
    """
    configure_logging()
    assert os.path.exists("logs"), "The 'logs' directory was not created."


def test_configure_logging_adds_handlers(clean_logs_dir):
    """
    Test that the `configure_logging` function adds file and console handlers to the logger.
    """
    with patch("logging.handlers.TimedRotatingFileHandler") as mock_file_handler, \
         patch("logging.StreamHandler") as mock_console_handler:
        mock_file_handler_instance = MagicMock()
        mock_console_handler_instance = MagicMock()
        mock_file_handler.return_value = mock_file_handler_instance
        mock_console_handler.return_value = mock_console_handler_instance

        logger = configure_logging()

        # Assert handlers are added to the logger
        assert mock_file_handler_instance in logger.handlers
        assert mock_console_handler_instance in logger.handlers


def test_configure_logging_logs_messages(clean_logs_dir):
    """
    Test that the logger logs messages correctly.
    """
    logger = configure_logging()
    log_file = f"logs/mangetamainapp_{datetime.now().strftime('%Y-%m-%d')}.log"
    test_message = "Test logging message."

    logger.info(test_message)

    # Check that the log file exists
    assert os.path.exists(log_file), "Log file was not created."

    # Verify the log message is written in the file
    with open(log_file, "r") as file:
        logs = file.read()
        assert test_message in logs, "Test message was not logged to the file."
