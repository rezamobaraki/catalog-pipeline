from pathlib import Path

from src.services import FileService, MappingService
from src.services.mapping_service import CompositeKey, MappingResult, SingleKey


class TestSingleFieldMapping:
    def test_transforms_value(self):
        """season=winter → season=Winter"""
        file_service = FileService()
        engine = MappingService(file_service)
        engine._single[SingleKey("season", "winter")] = MappingResult("season", "Winter")
        engine._mapped_fields.add("season")

        result = engine.apply({"season": "winter"})
        assert result["season"] == "Winter"

    def test_unmapped_passthrough(self):
        """Unmapped field passes through."""
        file_service = FileService()
        engine = MappingService(file_service)
        result = engine.apply({"brand": "Via Vai"})
        assert result["brand"] == "Via Vai"

    def test_empty_value_filtered(self):
        """Empty values not in output."""
        file_service = FileService()
        engine = MappingService(file_service)
        result = engine.apply({"catalog_code": ""})
        assert "catalog_code" not in result

    def test_mapped_field_no_match_not_passed(self):
        """Mapped field with no match doesn't passthrough."""
        file_service = FileService()
        engine = MappingService(file_service)
        engine._single[SingleKey("season", "winter")] = MappingResult("season", "Winter")
        engine._mapped_fields.add("season")

        result = engine.apply({"season": "autumn"})
        assert "season" not in result


class TestCompositeMapping:
    def test_transforms_value(self):
        """size_group_code=EU + size_code=36 → size=European size 36"""
        file_service = FileService()
        engine = MappingService(file_service)
        engine._composite[CompositeKey(("size_group_code", "size_code"), ("EU", "36"))] = MappingResult(
            "size", "European size 36"
        )
        engine._mapped_fields.update({"size_group_code", "size_code"})

        result = engine.apply({"size_group_code": "EU", "size_code": "36"})
        assert result["size"] == "European size 36"

    def test_partial_match_no_transform(self):
        """Partial match doesn't transform."""
        file_service = FileService()
        engine = MappingService(file_service)
        engine._composite[CompositeKey(("size_group_code", "size_code"), ("EU", "36"))] = MappingResult(
            "size", "European size 36"
        )
        engine._mapped_fields.update({"size_group_code", "size_code"})

        result = engine.apply({"size_group_code": "EU", "size_code": "37"})
        assert "size" not in result


class TestMappingServiceLoad:
    def test_load_single_mapping(self, tmp_path: Path):
        csv_content = "source;destination;source_type;destination_type\nwinter;Winter;season;season"
        csv_file = tmp_path / "mappings.csv"
        csv_file.write_text(csv_content)

        file_service = FileService()
        engine = MappingService(file_service)
        engine.load(csv_file)

        assert SingleKey("season", "winter") in engine._single
        assert engine._single[SingleKey("season", "winter")] == MappingResult("season", "Winter")

    def test_load_composite_mapping(self, tmp_path: Path):
        csv_content = (
            "source;destination;source_type;destination_type\n"
            "EU|36;European size 36;size_group_code|size_code;size"
        )
        csv_file = tmp_path / "mappings.csv"
        csv_file.write_text(csv_content)

        file_service = FileService()
        engine = MappingService(file_service)
        engine.load(csv_file)

        key = CompositeKey(("size_group_code", "size_code"), ("EU", "36"))
        assert key in engine._composite

    def test_mapped_fields_tracked(self, tmp_path: Path):
        csv_content = (
            "source;destination;source_type;destination_type\n"
            "winter;Winter;season;season\n"
            "EU|36;European size 36;size_group_code|size_code;size"
        )
        csv_file = tmp_path / "mappings.csv"
        csv_file.write_text(csv_content)

        file_service = FileService()
        engine = MappingService(file_service)
        engine.load(csv_file)

        assert "season" in engine._mapped_fields
        assert "size_group_code" in engine._mapped_fields
        assert "size_code" in engine._mapped_fields
