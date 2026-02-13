import logging
from pathlib import Path

from src.services.file_service import FileService

logger = logging.getLogger(__name__)


class MappingService:
	DELIMITER = "|"

	def __init__(self, file_service: FileService) -> None:
		self._file_service = file_service
		self._single: dict[tuple[str, str], tuple[str, str]] = {}
		self._composite: dict[tuple[tuple[str, ...], tuple[str, ...]], tuple[str, str]] = {}
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
		self._single[(src_type, src)] = (dst_type, dst)
		self._mapped_fields.add(src_type)

	def _add_composite(self, src_type: str, src: str, dst_type: str, dst: str) -> None:
		fields = tuple(src_type.split(self.DELIMITER))
		values = tuple(src.split(self.DELIMITER))

		if len(fields) != len(values):
			logger.warning(f"Mismatched composite mapping: {src_type}={src}")
			return

		self._composite[(fields, values)] = (dst_type, dst)
		self._mapped_fields.update(fields)

	def apply(self, row: dict[str, str]) -> dict[str, str]:
		result: dict[str, str] = {}

		# Apply single mappings
		for field, value in row.items():
			if value and (field, value) in self._single:
				dst_type, dst_value = self._single[(field, value)]
				result[dst_type] = dst_value

		# Apply composite mappings
		for (fields, values), (dst_type, dst_value) in self._composite.items():
			if all(row.get(f, "").strip() == v for f, v in zip(fields, values, strict=True)):
				result[dst_type] = dst_value

		# Passthrough unmapped fields
		for field, value in row.items():
			if value and field not in self._mapped_fields and field not in result:
				result[field] = value

		return result
