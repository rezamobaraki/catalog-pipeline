from collections import defaultdict
from collections.abc import Set
from typing import Any

Attributes = dict[str, Any]
NEVER_PROMOTE: frozenset[str] = frozenset({"ean", "article_id", "article_number"})


def _is_common(key: str, value: Any, items: list[Attributes]) -> bool:
    return all(item.get(key) == value for item in items)


def _remove_keys(item: Attributes, keys: Set[str]) -> Attributes:
    return {k: v for k, v in item.items() if k not in keys}


def find_common_attributes(
    items: list[Attributes], exclude: Set[str] = NEVER_PROMOTE
) -> Attributes:
    if not items:
        return {}

    first, *rest = items
    common = {}

    for key, value in first.items():
        if key in exclude or value is None:
            continue
        if _is_common(key, value, rest):
            common[key] = value

    return common


def promote_attributes(
    items: list[Attributes],
    exclude: Set[str] = NEVER_PROMOTE,
) -> tuple[Attributes, list[Attributes]]:
    common = find_common_attributes(items, exclude)
    remaining = [_remove_keys(item, common.keys()) for item in items]
    return common, remaining


def group_by_article(
    rows: list[dict[str, str]], key: str = "article_number"
) -> dict[str, list[dict[str, str]]]:
    groups = defaultdict(list)
    for row in rows:
        groups[row.get(key, "UNKNOWN")].append(row)
    return dict(groups)
