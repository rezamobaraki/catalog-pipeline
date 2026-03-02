import csv
from collections.abc import Iterator
from pathlib import Path

from src.domains import Catalog
from src.exceptions import FileReadError


class FileService:
    def read_csv(
        self, path: str | Path, delimiter: str = ";"
    ) -> Iterator[dict[str, str]]:
        path = Path(path)
        if not path.exists():
            raise FileReadError(f"File not found: {path}")

        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=delimiter)

                if not reader.fieldnames:
                    raise FileReadError(f"No header row found in {path}")

                for row in reader:
                    cleaned_row = {
                        k: v.strip() for k, v in row.items() if k and v is not None
                    }
                    if cleaned_row:
                        yield cleaned_row
        except UnicodeDecodeError as e:
            raise FileReadError(
                f"Cannot decode {path}. Ensure it is UTF-8 encoded. Error: {e}"
            )

    def write_json(self, catalog: Catalog, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(catalog.model_dump_json())
