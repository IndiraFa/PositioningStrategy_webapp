import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

def configure_logging(level="INFO"):
    """_summary_

    Args:
        level (str, optional): _description_. Defaults to "INFO".

    Returns:
        _type_: _description_
    """
    if not os.path.exists("logs"):
        os.makedirs("logs")

    
    # Configure the file rotation manager
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s"
    log_filename = f"logs/mangetamainapp_{datetime.now().strftime('%Y-%m-%d')}.log"
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
