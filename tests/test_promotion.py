from src.utils import NEVER_PROMOTE, find_common_attributes, promote_attributes


class TestFindCommonAttributes:
    def test_finds_common(self):
        items = [
            {"brand": "Nike", "size": "36"},
            {"brand": "Nike", "size": "37"},
        ]
        common = find_common_attributes(items)
        assert common == {"brand": "Nike"}

    def test_empty_list(self):
        assert find_common_attributes([]) == {}

    def test_single_item(self):
        items = [{"brand": "Nike", "size": "36"}]
        common = find_common_attributes(items)
        assert common == {"brand": "Nike", "size": "36"}

    def test_excludes_identity_fields(self):
        items = [
            {"ean": "123", "brand": "Nike"},
            {"ean": "123", "brand": "Nike"},
        ]
        common = find_common_attributes(items, exclude={"ean"})
        assert "ean" not in common
        assert common == {"brand": "Nike"}


class TestPromoteAttributes:
    def test_promotes_and_removes(self):
        items = [
            {"brand": "Nike", "size": "36"},
            {"brand": "Nike", "size": "37"},
        ]
        promoted, updated = promote_attributes(items)

        assert promoted == {"brand": "Nike"}
        assert all("brand" not in item for item in updated)
        assert updated[0] == {"size": "36"}

    def test_varying_stays(self):
        items = [
            {"brand": "Nike", "size": "36"},
            {"brand": "Nike", "size": "37"},
        ]
        promoted, updated = promote_attributes(items)

        assert "size" not in promoted
        assert updated[0]["size"] == "36"
        assert updated[1]["size"] == "37"

    def test_identity_never_promoted(self):
        items = [
            {"ean": "123", "brand": "Nike"},
            {"ean": "123", "brand": "Nike"},
        ]
        promoted, _ = promote_attributes(items, exclude=NEVER_PROMOTE)
        assert "ean" not in promoted

    def test_preserves_original(self):
        items = [{"brand": "Nike", "size": "36"}]
        original = [dict(item) for item in items]
        promote_attributes(items)
        assert items == original
