from __future__ import annotations
import logging
import uuid
from logging import Logger, NOTSET


def create_generation_id() -> str:
    """Generate a unique generation ID."""
    return str(uuid.uuid4())


class NullLogger(Logger):
    def __init__(self):
        super().__init__('null', level=NOTSET)


class StdErrLogger(Logger):
    def __init__(self, name: str = 'std_err_logger', level=logging.INFO):
        super().__init__(name, level=level)
        handler = logging.StreamHandler()
        handler.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s "%(message)s"')
        handler.setFormatter(formatter)
        if self.hasHandlers():
            self.handlers.clear()
        self.addHandler(handler)
