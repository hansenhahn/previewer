import hashlib
from pathlib import Path

from domain.fonts import load_font

FIXTURE = Path(__file__).parent / "fixtures" / "fonts" / "fontevent.NFTR"
KH_FIXTURE = Path(__file__).parent / "fixtures" / "fonts" / "font_eu_08.nftr"


def load_real_font():
    return load_font(FIXTURE.read_bytes())


def load_kh_font():
    return load_font(KH_FIXTURE.read_bytes())


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


def test_kh_font_header():
    # Fonte do KH 358/2 Days (1bpp, celula 7x8)
    font = load_kh_font()
    assert font.line_height == 8
    assert font.cell_width == 7
    assert font.cell_height == 8
    assert font.bpp == 1
    assert font.invalid_glyph_index == 0
    assert font.default_advance == 14


def test_kh_font_multisegment_cmap():
    # CMAP em dois segmentos encadeados: ASCII (32-126) + Latin-1 (acentos PT-BR).
    # Sem o encadeamento, o cmap ficaria em 95 (so ASCII).
    font = load_kh_font()
    assert len(font.glyphs) == 204
    assert len(font.cmap) == 204
    assert font.cmap[ord("A")] == 33
    for codepoint in (0xE1, 0xE3, 0xE7, 0xE9):  # á ã ç é
        assert codepoint in font.cmap
    assert font.glyph(ord("A")).advance == 5
