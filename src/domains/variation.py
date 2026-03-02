import logging
from decimal import Decimal, InvalidOperation
from typing import Any

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class Variation(BaseModel):
    ean: str
    attributes: dict[str, Any] = Field(default_factory=dict)

    @field_validator("ean")
    @classmethod
    def validate_ean_format(cls, v: str) -> str:
        if v and v != "UNKNOWN":
            if not v.isdigit():
                logger.warning("EAN must be numeric, got: %r — keeping original value", v)
            elif len(v) not in (8, 12, 13, 14):
                logger.warning("EAN should be 8/12/13/14 digits, got %d — keeping original value", len(v))
        return v

    @field_validator("attributes")
    @classmethod
    def validate_currency_field(cls, v: dict[str, Any]) -> dict[str, Any]:
        if currency := v.get("currency"):
            if not (len(currency) == 3 and currency.isalpha() and currency.isupper()):
                logger.warning("Currency should be 3-letter ISO code, got: %r — keeping original value", currency)
        return v

    @field_validator("attributes")
    @classmethod
    def validate_price_fields(cls, v: dict[str, Any]) -> dict[str, Any]:
        for price_field in ("price_buy_net", "price_sell"):
            if price_value := v.get(price_field):
                try:
                    if Decimal(str(price_value)) < 0:
                        logger.warning("%s is negative — keeping original value", price_field)
                except (InvalidOperation, ValueError):
                    logger.warning("%s is not a valid decimal — keeping original value", price_field)
        return v
