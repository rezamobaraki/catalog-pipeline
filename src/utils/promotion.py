from collections import defaultdict
from typing import Any

NEVER_PROMOTE = frozenset({"ean", "article_id", "article_number"})


def find_common_attributes(
    items: list[dict[str, Any]],
    exclude: set[str] | frozenset[str] | None = None,
) -> dict[str, Any]:
    if not items:
        return {}

    exclude = exclude or NEVER_PROMOTE
    first, *rest = items

    common = {}
    for key, value in first.items():
        if key in exclude or value is None:
            continue
        if all(item.get(key) == value for item in rest):
            common[key] = value

    return common


def promote_attributes(
    items: list[dict[str, Any]],
    exclude: set[str] | frozenset[str] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    common = find_common_attributes(items, exclude)
    cleaned = [{k: v for k, v in item.items() if k not in common} for item in items]
    return common, cleaned


def group_by_article(
    rows: list[dict[str, str]],
    key: str = "article_number",
) -> dict[str, list[dict[str, str]]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row.get(key, "UNKNOWN")].append(row)
    return dict(groups)
