import logging
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

from src.services.file_service import FileService

logger = logging.getLogger(__name__)


class SingleKey(NamedTuple):
    field: str
    value: str


class CompositeKey(NamedTuple):
    fields: tuple[str, ...]
    values: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MappingResult:
    field: str
    value: str


class MappingService:
    DELIMITER = "|"

    def __init__(self, file_service: FileService) -> None:
        self._file_service = file_service
        self._single: dict[SingleKey, MappingResult] = {}
        self._composite: dict[CompositeKey, MappingResult] = {}
        self._mapped_fields: set[str] = set()

    def load(self, path: str | Path) -> None:
        for row in self._file_service.read_csv(path):
            src = row.get("source", "").strip()
            dst = row.get("destination", "").strip()
            src_type = row.get("source_type", "").strip()
            dst_type = row.get("destination_type", "").strip()

            if not all([src, dst, src_type, dst_type]):
                logger.warning(f"Skipping incomplete row: {row}")
                continue

            if self.DELIMITER in src_type:
                self._add_composite(src_type, src, dst_type, dst)
            else:
                self._add_single(src_type, src, dst_type, dst)

    def _add_single(self, src_type: str, src: str, dst_type: str, dst: str) -> None:
        self._single[SingleKey(src_type, src)] = MappingResult(dst_type, dst)
        self._mapped_fields.add(src_type)

    def _add_composite(self, src_type: str, src: str, dst_type: str, dst: str) -> None:
        fields = tuple(src_type.split(self.DELIMITER))
        values = tuple(src.split(self.DELIMITER))

        if len(fields) != len(values):
            logger.warning(f"Mismatched composite mapping: {src_type}={src}")
            return

        self._composite[CompositeKey(fields, values)] = MappingResult(dst_type, dst)
        self._mapped_fields.update(fields)

    def apply(self, row: dict[str, str]) -> dict[str, str]:
        result: dict[str, str] = {}


        for field, value in row.items():
            if not value:
                logger.warning(f"Skipping empty value for field: {field}")
                continue

            if mapping := self._single.get(SingleKey(field, value)): # Apply single mappings
                result[mapping.field] = mapping.value

            elif value and field not in self._mapped_fields and field not in result: # Passthrough unmapped fields
                result[field] = value

        # Apply composite mappings
        for key, mapping in self._composite.items():
            if all(
                row.get(f, "").strip() == v
                for f, v in zip(key.fields, key.values, strict=True)
            ):
                result[mapping.field] = mapping.value

        return result
