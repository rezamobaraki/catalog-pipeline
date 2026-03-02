from pathlib import Path

from src.domains import Article, Catalog, Variation
from src.services.file_service import FileService
from src.services.mapping_service import MappingService
from src.utils import NEVER_PROMOTE, FieldCombiner, group_by_article, promote_attributes


class PipelineService:
	def __init__(self, file_service: FileService, combiner: FieldCombiner | None = None) -> None:
		self._file_service = file_service
		self._combiner = combiner

	def transform(
			self,
			pricat_path: str | Path,
			mappings_path: str | Path,
			article_key: str = "article_number",
	) -> Catalog:
		rows = self._read_and_map(pricat_path, mappings_path)
		if self._combiner:
			rows = [self._combiner.combine(row) for row in rows]
		articles = self._build_articles(rows, article_key)
		return self._build_catalog(articles)

	def _read_and_map(self, pricat_path: str | Path, mappings_path: str | Path) -> list[dict]:
		mapping = MappingService(self._file_service)
		mapping.load(mappings_path)
		return [mapping.apply(row) for row in self._file_service.read_csv(pricat_path)]

	def _build_articles(self, rows: list[dict], article_key: str) -> list[Article]:
		articles = []
		for article_id, variations in sorted(group_by_article(rows, article_key).items()):
			attrs, var_data = promote_attributes(variations, NEVER_PROMOTE)
			articles.append(Article(
				article_id=article_id,
				attributes=attrs,
				variations=[Variation(ean=v.pop("ean", "UNKNOWN"), attributes=v) for v in var_data],
			))
		return articles

	def _build_catalog(self, articles: list[Article]) -> Catalog:
		article_attrs = [a.attributes for a in articles]
		catalog_attrs, updated_attrs = promote_attributes(article_attrs, NEVER_PROMOTE)

		for article, attrs in zip(articles, updated_attrs, strict=True):
			article.attributes = attrs

		return Catalog(attributes=catalog_attrs, articles=articles)
