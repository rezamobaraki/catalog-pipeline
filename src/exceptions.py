class PricatError(Exception):
    pass


class ValidationError(PricatError):
    pass


class MappingError(PricatError):
    pass


class FileReadError(PricatError):
    pass
