import io

from PIL import Image

from domain.fonts import load_font

ATLAS_MIN_WIDTH = 256
PADDING = 1


def _placeholder(font):
    image = Image.new("RGBA", (ATLAS_MIN_WIDTH, max(font.line_height, 1)), (0, 0, 0, 0))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    metrics = {
        "line_height": font.line_height,
        "default_advance": getattr(font, "default_advance", 0),
        "image": {"width": image.width, "height": image.height},
        "glyphs": {},
    }
    return buffer.getvalue(), metrics


def generate(font_bytes: bytes):
    font = load_font(font_bytes)
    cmap = getattr(font, "cmap", {})

    unique = {}
    for codepoint, index in sorted(cmap.items()):
        if index in unique:
            continue
        glyph = font.glyph(codepoint)
        if glyph is not None and glyph.width > 0 and glyph.height > 0:
            unique[index] = glyph

    if not unique:
        return _placeholder(font)

    width = max(ATLAS_MIN_WIDTH, max(glyph.width for glyph in unique.values()))
    placements = {}
    x = y = row_height = 0
    for index, glyph in unique.items():
        if x + glyph.width > width and x > 0:
            x = 0
            y += row_height + PADDING
            row_height = 0
        placements[index] = (x, y, glyph.width, glyph.height)
        x += glyph.width + PADDING
        row_height = max(row_height, glyph.height)
    height = y + row_height

    atlas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for index, glyph in unique.items():
        gx, gy, gw, gh = placements[index]
        mask = Image.frombytes("L", (gw, gh), glyph.pixels)
        atlas.paste((255, 255, 255, 255), (gx, gy), mask)

    glyphs = {}
    for codepoint, index in sorted(cmap.items()):
        if index not in placements:
            continue
        glyph = font.glyph(codepoint)
        gx, gy, gw, gh = placements[index]
        glyphs[str(codepoint)] = {
            "index": index,
            "x": gx,
            "y": gy,
            "width": gw,
            "height": gh,
            "advance": glyph.advance,
            "leading": glyph.leading,
        }

    buffer = io.BytesIO()
    atlas.save(buffer, format="PNG")
    metrics = {
        "line_height": font.line_height,
        "default_advance": getattr(font, "default_advance", 0),
        "image": {"width": width, "height": height},
        "glyphs": glyphs,
    }
    return buffer.getvalue(), metrics
