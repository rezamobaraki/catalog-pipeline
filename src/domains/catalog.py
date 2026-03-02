import json
from typing import Any

from pydantic import BaseModel, Field, model_serializer

from src.domains.article import Article


class Catalog(BaseModel):
    attributes: dict[str, Any] = Field(default_factory=dict)
    articles: list[Article] = Field(default_factory=list)

    @model_serializer(mode="wrap")
    def _wrap(self, handler):
        return {"catalog": handler(self)}
