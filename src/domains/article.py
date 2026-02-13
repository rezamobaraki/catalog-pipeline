from typing import Any

from pydantic import BaseModel, Field

from src.domains.variation import Variation


class Article(BaseModel):
    article_id: str
    attributes: dict[str, Any] = Field(default_factory=dict)
    variations: list[Variation] = Field(default_factory=list)
