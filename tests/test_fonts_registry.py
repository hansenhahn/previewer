import pytest

from domain.errors import UnsupportedFontError
from domain.fonts import (
    Glyph,
    load_font,
    register,
    registered_formats,
)
from tests.fixtures.fonts.synth import build_nftr


class DummyFont:
    line_height = 3

    def glyph(self, codepoint, size=None):
        return Glyph(0, b"\x00", 1, 1, 1)

    def advance(self, codepoint):
        return 1


class DummyFormat:
    name = "dummy"

    def sniff(self, data):
        return data == b"DUMMY"

    def load(self, data):
        return DummyFont()


def test_registry_selects_matching_format():
    register(DummyFormat())
    assert isinstance(load_font(b"DUMMY"), DummyFont)


def test_registry_unknown_content_raises():
    with pytest.raises(UnsupportedFontError):
        load_font(b"NOPE")


def test_registered_formats_expose_contract():
    for fmt in registered_formats():
        assert isinstance(fmt.name, str)
        assert callable(fmt.sniff)
        assert callable(fmt.load)


def test_registered_nftr_adapts_generated_font():
    font = load_font(build_nftr())
    assert font.line_height == 8
    glyph = font.glyph(ord("A"))
    assert isinstance(glyph, Glyph)
    assert font.advance(ord("A")) == 4
