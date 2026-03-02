import logging
from typing import Any

from pydantic import BaseModel, Field, field_validator

from src.domains.variation import Variation

logger = logging.getLogger(__name__)


class Article(BaseModel):
    article_id: str
    attributes: dict[str, Any] = Field(default_factory=dict)
    variations: list[Variation] = Field(default_factory=list)

    @field_validator("article_id")
    @classmethod
    def validate_article_id_not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            logger.warning("article_id is empty — keeping original value")
        return value
