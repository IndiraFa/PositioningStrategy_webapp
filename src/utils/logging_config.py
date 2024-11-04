import os
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

def configure_logging(level = "INFO"):
    if not os.path.exists("logs"):
        os.makedirs("logs")

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_filename = f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log"


    file_handler = TimedRotatingFileHandler(
        log_filename,
        when="midnight",
        interval=1,
        backupCount=7
    )

    file_handler.setFormatter(logging.Formatter(log_format))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))

    # configuration of principal logger
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("logging configuration initiated")
    return logger