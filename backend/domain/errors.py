class DomainError(Exception):
    pass


class UnsupportedFontError(DomainError):
    pass


class FontDecodeError(DomainError):
    pass


class TextDecodeError(DomainError):
    pass


class TextEncodeError(DomainError):
    pass
