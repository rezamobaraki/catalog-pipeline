from pathlib import Path

from src.exceptions.base import PricatError


class FileError(PricatError):
    def __init__(self, path: str | Path, reason: str = "") -> None:
        self.path = Path(path)
        super().__init__(f"{self.path}: {reason}" if reason else str(self.path))


class FileReadError(FileError): ...


class FileWriteError(FileError): ...
