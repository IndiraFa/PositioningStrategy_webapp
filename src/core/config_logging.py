from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import os


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Configures a logging system for the application with file rotation.

    Creates a `logs` directory if it doesn't exist and sets up two handlers:
    - A file handler with daily rotation at midnight, keeping logs for 7 days.
    - A console handler to display logs in real-time.

    Args:
        level (int, optional): Minimum logging level for recording 
                               (e.g., `logging.INFO` or `logging.DEBUG`). Defaults to `logging.INFO`.

    Returns:
        logging.Logger: Configured logger instance for the application.
    """
    # Ensure the logs directory exists
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Log file format and name
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s"
    log_filename = f"logs/mangetamainapp_{datetime.now().strftime('%Y-%m-%d')}.log"

    # Configure file handler with daily rotation
    file_handler = TimedRotatingFileHandler(
        log_filename,
        when="midnight",
        interval=1,
        backupCount=7
    )
    file_handler.setFormatter(logging.Formatter(log_format))

    # Configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))

    # Set up the root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
