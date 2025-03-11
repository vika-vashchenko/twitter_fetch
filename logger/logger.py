import logging
import os

def setup_logger(log_file_path: str) -> logging.Logger:
    """
    Set up a logger that writes log messages to a specified file.

    Args:
        log_file_path (str): The path to the log file.

    Returns:
        logging.Logger: Configured logger instance.
    """
    log_folder = os.path.dirname(log_file_path)
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    logging.basicConfig(
        filename=log_file_path,
        level=logging.INFO,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )
    logger = logging.getLogger()
    return logger