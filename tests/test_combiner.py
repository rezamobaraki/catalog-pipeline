from src.utils import FieldCombiner


class TestFieldCombiner:
    def test_combines_and_removes_originals(self):
        """price_buy_net + currency → price_buy_net_currency='58.5 EUR'"""
        combiner = FieldCombiner([("price_buy_net", "currency")])
        result = combiner.combine({"price_buy_net": "58.5", "currency": "EUR", "ean": "123"})

        assert result["price_buy_net_currency"] == "58.5 EUR"
        assert "price_buy_net" not in result
        assert "currency" not in result
        assert result["ean"] == "123"

    def test_skips_when_field_missing(self):
        """Does not combine when a field is missing."""
        combiner = FieldCombiner([("price_buy_net", "currency")])
        result = combiner.combine({"price_buy_net": "58.5", "ean": "123"})

        assert "price_buy_net_currency" not in result
        assert result["price_buy_net"] == "58.5"

    def test_multiple_specs(self):
        """Multiple combine specs applied."""
        combiner = FieldCombiner([("a", "b"), ("c", "d")])
        result = combiner.combine({"a": "1", "b": "2", "c": "3", "d": "4", "e": "5"})

        assert result["a_b"] == "1 2"
        assert result["c_d"] == "3 4"
        assert result["e"] == "5"

    def test_three_fields(self):
        """Combining three fields works."""
        combiner = FieldCombiner([("a", "b", "c")])
        result = combiner.combine({"a": "1", "b": "2", "c": "3"})

        assert result["a_b_c"] == "1 2 3"

    def test_parse_spec(self):
        assert FieldCombiner.parse_spec("price_buy_net,currency") == ["price_buy_net", "currency"]
        assert FieldCombiner.parse_spec("a, b , c") == ["a", "b", "c"]

    def test_empty_value_skips(self):
        combiner = FieldCombiner([("a", "b")])
        result = combiner.combine({"a": "1", "b": ""})

        assert "a_b" not in result


