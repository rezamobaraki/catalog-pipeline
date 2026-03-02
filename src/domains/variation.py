from decimal import Decimal, InvalidOperation
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Variation(BaseModel):
    ean: str
    attributes: dict[str, Any] = Field(default_factory=dict)

    @field_validator("ean")
    @classmethod
    def validate_ean_format(cls, v: str) -> str:
        if v and v != "UNKNOWN":
            if not v.isdigit():
                raise ValueError(f"EAN must be numeric, got: {v!r}")
            if len(v) not in (8, 12, 13, 14):
                raise ValueError(f"EAN must be 8/12/13/14 digits, got {len(v)}")
        return v

    @field_validator("attributes")
    @classmethod
    def validate_currency_field(cls, v: dict[str, Any]) -> dict[str, Any]:
        if currency := v.get("currency"):
            if not (len(currency) == 3 and currency.isalpha() and currency.isupper()):
                raise ValueError(f"Currency must be 3-letter ISO code, got: {currency!r}")
        return v

    @field_validator("attributes")
    @classmethod
    def validate_price_fields(cls, v: dict[str, Any]) -> dict[str, Any]:
        for price_field in ("price_buy_net", "price_sell"):
            if price_value := v.get(price_field):
                try:
                    if Decimal(str(price_value)) < 0:
                        raise ValueError(f"{price_field} cannot be negative")
                except (InvalidOperation, ValueError):
                    pass  # Lenient validation, keep original value
        return v
