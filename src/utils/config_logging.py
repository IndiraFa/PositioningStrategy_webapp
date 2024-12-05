import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler


def configure_logging(level=logging.INFO):
    """
    Configures a logging system for the application with file rotation.

    Creates a `logs` directory if it doesn't exist and sets up two handlers:
    - A file handler with daily rotation at midnight, keeping logs for 7 days.
    - A console handler to display logs in real-time.

    Args:
        level (int, optional): Minimum logging level for recording
        (e.g., `logging.INFO` or `logging.DEBUG`).
                               Defaults to `logging.INFO`.

    Returns:
        logging.Logger: Configured logger instance for the application.
    """
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Configure the file rotation manager
    log_format = """
        %(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s
    """
    log_filename = f"""
        logs/mangetamainapp_{datetime.now().strftime('%Y-%m-%d')}.log
    """
    file_handler = TimedRotatingFileHandler(
        log_filename,
        when="midnight",
        interval=1,
        backupCount=7
    )

    file_handler.setFormatter(logging.Formatter(log_format))

    # Configure the log manager for the console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))

    # Configurer le logger principal
    logger = logging.getLogger("app")
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.info("Logging configuration set")
    return logger