import csv
from collections.abc import Iterator
from pathlib import Path

from domains import Catalog


class FileService:
    """Handles all file I/O operations."""

    def read_csv(self, path: str | Path, delimiter: str = ",") -> Iterator[dict[str, str]]:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                yield {k: v.strip() for k, v in row.items() if k is not None}

    def write_json(self, catalog: Catalog, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(catalog.to_json())
