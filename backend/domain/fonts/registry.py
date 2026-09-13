from .base import Font, FontFormat
from ..errors import UnsupportedFontError

_formats: list[FontFormat] = []


def register(fmt: FontFormat) -> None:
    if any(existing.name == fmt.name for existing in _formats):
        return
    _formats.append(fmt)


def registered_formats() -> tuple[FontFormat, ...]:
    return tuple(_formats)


def load_font(data: bytes) -> Font:
    for fmt in _formats:
        if fmt.sniff(data):
            return fmt.load(data)
    raise UnsupportedFontError("formato de fonte não suportado")
