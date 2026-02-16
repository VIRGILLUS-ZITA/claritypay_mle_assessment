import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger():

    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger("featurelog")
    logger.setLevel(logging.INFO)

    # prevent duplicate handlers if re-run
    if logger.handlers:
        return logger

    # ---- console handler ----
    console_handler = logging.StreamHandler()
    console_format = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        "%H:%M:%S"
    )
    console_handler.setFormatter(console_format)

    # ---- file handler ----
    file_handler = RotatingFileHandler(
        "logs/featurelog.log",
        maxBytes=1_000_000,
        backupCount=3
    )
    file_format = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

def setup_logger_run():

    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger("mainpipeline_log")
    logger.setLevel(logging.INFO)

    # prevent duplicate handlers if re-run
    if logger.handlers:
        return logger

    # ---- console handler ----
    console_handler = logging.StreamHandler()
    console_format = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        "%H:%M:%S"
    )
    console_handler.setFormatter(console_format)

    # ---- file handler ----
    file_handler = RotatingFileHandler(
        "logs/mainpipeline_log.log",
        maxBytes=1_000_000,
        backupCount=3
    )
    file_format = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
