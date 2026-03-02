import json
from pathlib import Path

import pytest

from src.services import FileService, PipelineService


class TestTransformCatalog:
    def test_full_transformation(self, data_dir: Path):
        pricat = data_dir / "pricat.csv"
        mappings = data_dir / "mappings.csv"

        if not pricat.exists() or not mappings.exists():
            pytest.skip("Data files not available")

        file_service = FileService()
        pipeline = PipelineService(file_service)
        catalog = pipeline.transform(pricat, mappings)

        assert len(catalog.articles) > 0
        assert "brand" in catalog.attributes
        assert catalog.attributes["brand"] == "Via Vai"
        assert catalog.attributes["season"] == "Winter"

    def test_articles_structure(self, data_dir: Path):
        pricat = data_dir / "pricat.csv"
        mappings = data_dir / "mappings.csv"

        if not pricat.exists() or not mappings.exists():
            pytest.skip("Data files not available")

        file_service = FileService()
        pipeline = PipelineService(file_service)
        catalog = pipeline.transform(pricat, mappings)

        article = next((a for a in catalog.articles if a.article_id == "15189-02"), None)
        assert article is not None
        assert len(article.variations) > 1

        for var in article.variations:
            assert var.ean != "UNKNOWN"

    def test_size_mapping(self, data_dir: Path):
        pricat = data_dir / "pricat.csv"
        mappings = data_dir / "mappings.csv"

        if not pricat.exists() or not mappings.exists():
            pytest.skip("Data files not available")

        file_service = FileService()
        pipeline = PipelineService(file_service)
        catalog = pipeline.transform(pricat, mappings)
        variation = catalog.articles[0].variations[0]

        assert "size" in variation.attributes
        assert "European size" in variation.attributes["size"]

    def test_json_valid(self, data_dir: Path):
        pricat = data_dir / "pricat.csv"
        mappings = data_dir / "mappings.csv"

        if not pricat.exists() or not mappings.exists():
            pytest.skip("Data files not available")

        file_service = FileService()
        pipeline = PipelineService(file_service)
        catalog = pipeline.transform(pricat, mappings)
        data = json.loads(catalog.to_json())

        assert "catalog" in data
        assert "attributes" in data["catalog"]
        assert "articles" in data["catalog"]


class TestEdgeCases:
    def test_empty_values_filtered(self, data_dir: Path):
        pricat = data_dir / "pricat.csv"
        mappings = data_dir / "mappings.csv"

        if not pricat.exists() or not mappings.exists():
            pytest.skip("Data files not available")

        file_service = FileService()
        pipeline = PipelineService(file_service)
        catalog = pipeline.transform(pricat, mappings)
        assert "catalog_code" not in catalog.attributes

    def test_price_varies_within_article(self, data_dir: Path):
        pricat = data_dir / "pricat.csv"
        mappings = data_dir / "mappings.csv"

        if not pricat.exists() or not mappings.exists():
            pytest.skip("Data files not available")

        file_service = FileService()
        pipeline = PipelineService(file_service)
        catalog = pipeline.transform(pricat, mappings)

        article = next((a for a in catalog.articles if a.article_id == "15189-02"), None)
        assert article is not None
        assert "price_buy_net" not in article.attributes

        prices = {v.attributes.get("price_buy_net") for v in article.variations}
        assert len(prices) > 1
