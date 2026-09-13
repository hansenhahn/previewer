from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class Glyph:
    index: int
    pixels: bytes
    width: int
    height: int
    advance: int
    leading: int = 0


@runtime_checkable
class Font(Protocol):
    line_height: int

    def glyph(self, codepoint: int, size: int | None = None) -> Glyph | None: ...

    def advance(self, codepoint: int) -> int: ...


@runtime_checkable
class FontFormat(Protocol):
    name: str

    def sniff(self, data: bytes) -> bool: ...

    def load(self, data: bytes) -> Font: ...
