import json
from typing import Any

from pydantic import BaseModel, Field

from .article import Article


class Catalog(BaseModel):
    attributes: dict[str, Any] = Field(default_factory=dict)
    articles: list[Article] = Field(default_factory=list)

    def to_json(self, indent: int = 2) -> str:
        data = {"catalog": self.model_dump()}
        return json.dumps(data, indent=indent, sort_keys=True, ensure_ascii=False)
