class FieldCombiner:

    def __init__(self, combinations: list[tuple[str, ...]], separator: str = " ") -> None:
        self._combinations = combinations
        self._separator = separator

    def combine(self, row: dict[str, str]) -> dict[str, str]:
        result = dict(row)

        for fields in self._combinations:
            values = [result.get(f, "") for f in fields]

            if all(values):
                combined_key = "_".join(fields)
                combined_value = self._separator.join(values)

                for field in fields:
                    result.pop(field, None)

                result[combined_key] = combined_value

        return result
