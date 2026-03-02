from typing import Any

from pydantic import BaseModel, Field

from src.domains.article import Article


class Catalog(BaseModel):
    attributes: dict[str, Any] = Field(default_factory=dict)
    articles: list[Article] = Field(default_factory=list)

    def to_json(self) -> str:
        wrapper = CatalogWrapper(catalog=self)
        return wrapper.model_dump_json(indent=4)


class CatalogWrapper(BaseModel):
    catalog: Catalog
