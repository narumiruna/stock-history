import logging
import os
from pathlib import Path

FORMAT = '[%(asctime)s][%(levelname)s][%(name)s] %(message)s'
DATE_FORMAT = '%Y-%m-%d_%H:%M:%S'

LEVEL_MAP = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOSET': logging.NOTSET,
}


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    # set level
    level = LEVEL_MAP.get(os.getenv('LOG_LEVEL', default='INFO'))
    logger.setLevel(level)

    # formatter
    formatter = logging.Formatter(FORMAT, datefmt=DATE_FORMAT)

    # stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # file handler
    log_file = os.getenv('LOG_TO_FILE')
    if log_file is not None:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # prevent twice log
    logger.propagate = False
    return logger
