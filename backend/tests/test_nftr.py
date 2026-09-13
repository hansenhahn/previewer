import pytest

from domain.errors import FontDecodeError
from domain.fonts import load_font
from tests.fixtures.fonts.synth import build_nftr

EXPECTED_A_PIXELS = bytes(
    [
        0, 255, 255, 0, 0, 0, 0, 0,
        255, 0, 0, 255, 0, 0, 0, 0,
        255, 255, 255, 255, 0, 0, 0, 0,
        255, 0, 0, 255, 0, 0, 0, 0,
    ]
)


def test_reads_header_and_mapping():
    font = load_font(build_nftr())
    assert font.cell_width == 4
    assert font.cell_height == 4
    assert font.bpp == 1
    assert font.line_height == 8
    assert font.cmap == {0x41: 1}


def test_decodes_glyph_bitmap_golden():
    font = load_font(build_nftr())
    glyph = font.glyph(ord("A"))
    assert glyph.width == 8
    assert glyph.height == 4
    assert glyph.advance == 4
    assert glyph.pixels == EXPECTED_A_PIXELS


def test_advance_uses_cwdh():
    font = load_font(build_nftr())
    assert font.advance(ord("A")) == 4


def test_unmapped_codepoint_uses_default_advance():
    font = load_font(build_nftr())
    glyph = font.glyph(ord("Z"))
    assert glyph is not None
    assert glyph.advance == font.default_advance
    assert len(glyph.pixels) == glyph.width * glyph.height


def test_truncated_font_raises():
    with pytest.raises(FontDecodeError):
        load_font(b"RTFN" + b"\x00" * 5)
