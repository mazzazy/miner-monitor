import logging
import os
from datetime import datetime


class LoggerFactory:

    @staticmethod
    def get_logger(name: str):

        # Ensure logs folder exists
        os.makedirs("logs", exist_ok=True)

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        # Prevent duplicate handlers (VERY important in imports)
        if logger.handlers:
            return logger

        # -------------------------
        # File handler
        # -------------------------
        log_file = f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log"

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # -------------------------
        # Console handler
        # -------------------------
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # -------------------------
        # Format
        # -------------------------
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger