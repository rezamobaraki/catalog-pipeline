
import json
from typing import Any

from pydantic import BaseModel, Field


class Variation(BaseModel):
    ean: str
    attributes: dict[str, Any] = Field(default_factory=dict)


class Article(BaseModel):
    article_id: str
    attributes: dict[str, Any] = Field(default_factory=dict)
    variations: list[Variation] = Field(default_factory=list)


class Catalog(BaseModel):
    attributes: dict[str, Any] = Field(default_factory=dict)
    articles: list[Article] = Field(default_factory=list)

    def to_json(self, indent: int = 2) -> str:
        data = {"catalog": self.model_dump()}
        return json.dumps(data, indent=indent, sort_keys=True, ensure_ascii=False)
