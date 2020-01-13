"""This module is responsible for saving logs to the logs.log file."""

import logging
FILENAME = 'logs.log'
FORMAT = '%(levelname)s: %(asctime)s %(message)s'

def log_info(message: str) -> None:
    """
    Logs info such as an alarm going off, weather change or a news
    news story.
    """
    logging.basicConfig(filename=FILENAME, level=logging.DEBUG,
                        format=FORMAT)
    logging.info(message)

def log_warning(message: str) -> None:
    """
    logs warnings such as attempting to load an empty json file.
    """
    logging.basicConfig(filename=FILENAME, level=logging.DEBUG,
                        format=FORMAT)
    logging.warning(message)

def log_error(message: str) -> None:
    """
    Logs known potential errors such as a RuntimeError while text to
    speech is in use.
    """
    logging.basicConfig(filename=FILENAME, level=logging.DEBUG,
                        format=FORMAT)
    logging.error(message)
