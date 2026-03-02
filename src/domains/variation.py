from decimal import Decimal, InvalidOperation
from typing import Any

from pydantic import BaseModel, Field, field_validator

from src.exceptions import ValidationError


class Variation(BaseModel):
    ean: str
    attributes: dict[str, Any] = Field(default_factory=dict)

    @field_validator("ean")
    @classmethod
    def validate_ean_format(cls, value: str) -> str:
        if value and value != "UNKNOWN":
            if not value.isdigit():
                raise ValidationError(
                    f"EAN must be numeric, got: {value!r}",
                    field="ean",
                    value=value,
                )
            if len(value) not in (8, 12, 13, 14):
                raise ValidationError(
                    f"EAN must be 8/12/13/14 digits, got {len(value)}",
                    field="ean",
                    value=value,
                )
        return value

    @field_validator("attributes")
    @classmethod
    def validate_currency_field(cls, value: dict[str, Any]) -> dict[str, Any]:
        if currency := value.get("currency"):
            if not (len(currency) == 3 and currency.isalpha() and currency.isupper()):
                raise ValidationError(
                    f"Currency must be 3-letter ISO code, got: {currency!r}",
                    field="currency",
                    value=currency,
                )
        return value

    @field_validator("attributes")
    @classmethod
    def validate_price_fields(cls, value: dict[str, Any]) -> dict[str, Any]:
        for price_field in ("price_buy_net", "price_sell"):
            if price_value := value.get(price_field):
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
        return value
