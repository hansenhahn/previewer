import json
from pathlib import Path

import pytest

from domain.fonts.base import Glyph
from domain.layout import ScreenConfig, layout

CASES = json.loads(
    (Path(__file__).parents[2] / "frontend" / "src" / "layout_cases.json").read_text(
        encoding="utf-8"
    )
)


class AtlasFont:
    def __init__(self, atlas: dict):
        self.atlas = atlas
        self.line_height = atlas["line_height"]

    def glyph(self, codepoint, size=None):
        entry = self.atlas["glyphs"].get(str(codepoint))
        if entry is None:
            return Glyph(-1, b"", 0, 0, self.atlas["default_advance"], 0)
        return Glyph(
            entry["index"],
            b"",
            entry["width"],
            entry["height"],
            entry["advance"],
            entry["leading"],
        )

    def advance(self, codepoint):
        return self.glyph(codepoint).advance


def _config(case: dict) -> ScreenConfig:
    screen = CASES["screen"]
    return ScreenConfig(
        x_pos=screen["x"],
        y_pos=screen["y"],
        new_line=case.get("new_line", screen["new_line"]),
        matches=tuple(case["matches"]),
        tags=tuple(case["tags"]),
    )


@pytest.mark.parametrize("case", CASES["cases"], ids=lambda case: case["name"])
def test_layout_conformance(case):
    result = layout(
        case["text"], AtlasFont(CASES["atlas"]), _config(case), cursor_line=case["cursor_line"]
    )
    expected = case["expected"]
    if "glyph_count" in expected:
        assert len(result.glyphs) == expected["glyph_count"]
    else:
        assert [
            {"codepoint": placed.codepoint, "x": placed.x, "y": placed.y}
            for placed in result.glyphs
        ] == expected["glyphs"]
    assert result.overflow_horizontal is expected["overflow_horizontal"]
    assert result.overflow_vertical is expected["overflow_vertical"]
