from typing import Any

from pydantic import BaseModel, Field, field_validator

from src.domains.variation import Variation
from src.exceptions import ValidationError


class Article(BaseModel):
    article_id: str
    attributes: dict[str, Any] = Field(default_factory=dict)
    variations: list[Variation] = Field(default_factory=list)

    @field_validator("article_id")
    @classmethod
    def validate_article_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValidationError(
                "article_id cannot be empty",
                field="article_id",
                value=v,
            )
        return v
