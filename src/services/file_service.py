import csv
from collections.abc import Iterator
from pathlib import Path

from src.domains import Catalog
from src.exceptions import FileReadError, FileWriteError


class FileService:
	def read_csv(self, path: str | Path, delimiter: str = ";") -> Iterator[dict[str, str]]:
		try:
			with open(path, newline="", encoding="utf-8") as f:
				reader = csv.DictReader(f, delimiter=delimiter)
				for row in reader:
					yield {k: v.strip() for k, v in row.items() if k is not None and v is not None}
		except OSError as exc:
			raise FileReadError(path, reason=str(exc)) from exc

	def write_json(self, catalog: Catalog, path: str | Path) -> None:
		path = Path(path)
		try:
			path.parent.mkdir(parents=True, exist_ok=True)
			with open(path, "w", encoding="utf-8") as f:
				f.write(catalog.to_json())
		except OSError as exc:
			raise FileWriteError(path, reason=str(exc)) from exc
