from typing import Any

from src.exceptions.base import PricatError


class ValidationError(PricatError):
    def __init__(self, message: str, *, field: str = "", value: Any = None) -> None:
        self.field = field
        self.value = value
        super().__init__(message)
