from pathlib import Path

import pytest

from domain.errors import UnsupportedFontError
from infra.atlas import generate

FONT_FIXTURE = Path(__file__).parent / "fixtures" / "fonts" / "fontevent.NFTR"


def test_generate_png_and_metrics():
    png, metrics = generate(FONT_FIXTURE.read_bytes())
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert metrics["line_height"] == 12
    assert metrics["image"]["width"] >= 256

    glyphs = metrics["glyphs"]
    assert glyphs
    entry = glyphs[str(ord("A"))]
    assert entry["index"] == 31
    assert entry["height"] == 12
    assert entry["width"] > 0
    assert entry["advance"] == 7


def test_generate_rejects_unknown_font():
    with pytest.raises(UnsupportedFontError):
        generate(b"nao e uma fonte")
