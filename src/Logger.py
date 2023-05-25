import logging
import sys


class Logger:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.error_logger = logging.getLogger("Semantic Error")
        formatter = logging.Formatter('Semantic Error: %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.error_logger.addHandler(handler)

        self.warning_logger = logging.getLogger("Semantic Warning")
        formatter = logging.Formatter('Semantic Warning: %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.warning_logger.addHandler(handler)

    def log_warning(self, message):
        self.warning_logger.warning(message)

    def log_error(self, message):
        self.error_logger.error(message)
        sys.exit()
