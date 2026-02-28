from decimal import Decimal, InvalidOperation
from typing import Any

from pydantic import BaseModel, Field, field_validator

from src.exceptions import ValidationError


class Variation(BaseModel):
    ean: str
    attributes: dict[str, Any] = Field(default_factory=dict)

    @field_validator("ean")
    @classmethod
    def validate_ean_format(cls, v: str) -> str:
        if v and v != "UNKNOWN":
            if not v.isdigit():
                raise ValidationError(
                    f"EAN must be numeric, got: {v!r}",
                    field="ean",
                    value=v,
                )
            if len(v) not in (8, 12, 13, 14):
                raise ValidationError(
                    f"EAN must be 8/12/13/14 digits, got {len(v)}",
                    field="ean",
                    value=v,
                )
        return v

    @field_validator("attributes")
    @classmethod
    def validate_currency_field(cls, v: dict[str, Any]) -> dict[str, Any]:
        if currency := v.get("currency"):
            if not (len(currency) == 3 and currency.isalpha() and currency.isupper()):
                raise ValidationError(
                    f"Currency must be 3-letter ISO code, got: {currency!r}",
                    field="currency",
                    value=currency,
                )
        return v

    @field_validator("attributes")
    @classmethod
    def validate_price_fields(cls, v: dict[str, Any]) -> dict[str, Any]:
        for price_field in ("price_buy_net", "price_sell"):
            if price_value := v.get(price_field):
                try:
                    if Decimal(str(price_value)) < 0:
                        raise ValidationError(
                            f"{price_field} cannot be negative",
                            field=price_field,
                            value=price_value,
                        )
                except (InvalidOperation, ValidationError):
                    if isinstance(price_value, str):
                        pass  # Lenient validation, keep original value
                    else:
                        raise
        return v
