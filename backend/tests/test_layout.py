from domain.fonts import Glyph
from domain.layout import PlacedGlyph, ScreenConfig, layout


class DummyFont:
    line_height = 8

    def __init__(self, advance=2, leading=0):
        self.advance_value = advance
        self.leading = leading

    def glyph(self, codepoint, size=None):
        return Glyph(codepoint, b"\x00", 2, 2, self.advance_value, self.leading)

    def advance(self, codepoint):
        return self.advance_value


def make_config(**overrides):
    base = dict(x_pos=0, y_pos=0, new_line=8)
    base.update(overrides)
    return ScreenConfig(**base)


def test_screen_config_and_placed_glyph_creation():
    config = make_config()
    placed = PlacedGlyph(ord("A"), 1, 2, DummyFont().glyph(ord("A")))
    assert config.width == 256
    assert config.height == 192
    assert placed.codepoint == ord("A")


def test_positions_and_line_wrap():
    result = layout("AB", DummyFont(advance=2), make_config())
    assert [p.x for p in result.glyphs] == [0, 3]
    assert [p.y for p in result.glyphs] == [0, 0]

    multi = layout("A\nB", DummyFont(advance=2), make_config())
    assert [p.y for p in multi.glyphs] == [0, 8]


def test_overflow_horizontal():
    result = layout("AAA", DummyFont(advance=1), make_config(width=3))
    assert result.overflow_horizontal is True
    assert len(result.glyphs) == 2


def test_overflow_vertical():
    result = layout("A\nB\nC", DummyFont(), make_config(height=8))
    assert result.overflow_vertical is True
    assert len(result.glyphs) == 2


def test_pivot_found():
    text = "header\nMATCH\nbody"
    result = layout(
        text,
        DummyFont(),
        make_config(matches=("MATCH",)),
        cursor_line=2,
    )
    assert "".join(chr(p.codepoint) for p in result.glyphs) == "body"


def test_without_pivot_starts_at_beginning():
    result = layout(
        "header\nbody",
        DummyFont(),
        make_config(matches=("NOPE",)),
        cursor_line=5,
    )
    assert "".join(chr(p.codepoint) for p in result.glyphs) == "headerbody"


def test_tags_are_removed_before_measurement():
    with_tag = layout("A<tag>B", DummyFont(advance=2), make_config(tags=("<tag>",)))
    without_tag = layout("AB", DummyFont(advance=2), make_config())
    assert [p.codepoint for p in with_tag.glyphs] == [ord("A"), ord("B")]
    assert [p.x for p in with_tag.glyphs] == [p.x for p in without_tag.glyphs]


def test_layout_uses_font_abstraction():
    result = layout("AB", DummyFont(advance=5, leading=1), make_config())
    assert [p.x for p in result.glyphs] == [1, 7]
