import hashlib
from pathlib import Path

from domain.fonts import load_font

FIXTURE = Path(__file__).parent / "fixtures" / "fonts" / "fontevent.NFTR"


def load_real_font():
    return load_font(FIXTURE.read_bytes())


def test_real_font_header():
    font = load_real_font()
    assert font.line_height == 12
    assert font.cell_width == 9
    assert font.cell_height == 12
    assert font.bpp == 1
    assert font.invalid_glyph_index == 0
    assert font.default_advance == 18


def test_real_font_glyph_count_matches_cmap():
    font = load_real_font()
    assert len(font.glyphs) == 158
    assert len(font.cmap) == 158


def test_real_font_glyph_a_golden():
    font = load_real_font()
    glyph = font.glyph(ord("A"))
    assert (glyph.index, glyph.width, glyph.height, glyph.advance, glyph.leading) == (
        31,
        16,
        12,
        7,
        0,
    )
    assert hashlib.sha256(glyph.pixels).hexdigest() == (
        "1caac671ac3e176c772d5d8c3dc5b12065e886713a204a1332062faea7837d05"
    )


def test_real_font_blank_space():
    font = load_real_font()
    glyph = font.glyph(ord(" "))
    assert not any(glyph.pixels)
    assert font.advance(ord(" ")) == 3
