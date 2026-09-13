import re
from dataclasses import dataclass

from .fonts.base import Font, Glyph

SCREEN_WIDTH = 256
SCREEN_HEIGHT = 192


@dataclass(frozen=True, slots=True)
class ScreenConfig:
    x_pos: int
    y_pos: int
    new_line: int
    width: int = SCREEN_WIDTH
    height: int = SCREEN_HEIGHT
    matches: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PlacedGlyph:
    codepoint: int
    x: int
    y: int
    glyph: Glyph


@dataclass(frozen=True, slots=True)
class LayoutResult:
    glyphs: tuple[PlacedGlyph, ...]
    overflow_horizontal: bool = False
    overflow_vertical: bool = False


def _strip_tags(line: str, tags: tuple[str, ...]) -> str:
    for tag in tags:
        line = re.sub(tag, "", line)
    return line


def _pivot_line(lines: list[str], matches: tuple[str, ...], cursor_line: int) -> int:
    index = min(cursor_line, len(lines) - 1)
    while index >= 0:
        if any(re.match(pattern, lines[index]) for pattern in matches):
            return index + 1
        index -= 1
    return 0


def layout(text: str, font: Font, config: ScreenConfig, cursor_line: int = 0) -> LayoutResult:
    lines = text.split("\n")
    start = _pivot_line(lines, config.matches, cursor_line) if config.matches else 0

    placed: list[PlacedGlyph] = []
    overflow_horizontal = False
    overflow_vertical = False
    y = config.y_pos

    for line in lines[start:]:
        if y > config.height:
            overflow_vertical = True
            break

        x = config.x_pos
        for char in _strip_tags(line, config.tags):
            codepoint = ord(char)
            glyph = font.glyph(codepoint)
            if glyph is None:
                continue
            placed.append(PlacedGlyph(codepoint, x + glyph.leading, y, glyph))
            x += glyph.advance + 1
            if x > config.width:
                overflow_horizontal = True
                break
        y += config.new_line

    return LayoutResult(tuple(placed), overflow_horizontal, overflow_vertical)
