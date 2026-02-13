from typing import Any

from pydantic import BaseModel, Field


class Variation(BaseModel):
    ean: str
    attributes: dict[str, Any] = Field(default_factory=dict)
