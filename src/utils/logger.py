import logging


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger using the given name (pass __name__)."""
    return logging.getLogger(name)
