import struct

CELL_WIDTH = 4
CELL_HEIGHT = 4
BPP = 1
CELL_SIZE = (CELL_WIDTH * CELL_HEIGHT * BPP + 7) // 8
LINE_HEIGHT = 8
CODEPOINT_A = 0x41
GLYPH_INDEX_A = 1
GLYPH_BYTES_A = bytes([0x69, 0xF9])


def build_nftr() -> bytes:
    finf_start = 16
    finf_data_size = 24
    cglp_start = finf_start + 8 + finf_data_size
    cglp_data_size = 8 + CELL_SIZE * 2
    cwdh_start = cglp_start + 8 + cglp_data_size
    cwdh_data_size = 8 + 3 * 2
    cmap_start = cwdh_start + 8 + cwdh_data_size
    cmap_data_size = 12 + 2
    total = cmap_start + 8 + cmap_data_size

    cglp_offset = cglp_start + 8
    cwdh_offset = cwdh_start + 8
    cmap_offset = cmap_start + 8

    out = bytearray()
    out += b"RTFN"
    out += struct.pack("<HH", 0xFEFF, 0x0100)
    out += struct.pack("<I", total)
    out += struct.pack("<H", 16)
    out += struct.pack("<H", 4)

    assert len(out) == finf_start
    out += b"FNIF"
    out += struct.pack("<I", 8 + finf_data_size)
    out += struct.pack("<B", 0)
    out += struct.pack("<B", LINE_HEIGHT)
    out += struct.pack("<H", 0)
    out += struct.pack("<b", 0)
    out += struct.pack("<B", CELL_WIDTH)
    out += struct.pack("<b", 0)
    out += struct.pack("<B", 3)
    out += struct.pack("<I", cglp_offset)
    out += struct.pack("<I", cwdh_offset)
    out += struct.pack("<I", cmap_offset)
    out += b"\x00" * (finf_data_size - 20)

    assert len(out) == cglp_start
    out += b"PLGC"
    out += struct.pack("<I", 8 + cglp_data_size)
    out += struct.pack("<B", CELL_WIDTH)
    out += struct.pack("<B", CELL_HEIGHT)
    out += struct.pack("<H", CELL_SIZE)
    out += struct.pack("<B", 0)
    out += struct.pack("<B", CELL_WIDTH)
    out += struct.pack("<B", BPP)
    out += struct.pack("<B", 0)
    out += bytes(CELL_SIZE)
    out += GLYPH_BYTES_A

    assert len(out) == cwdh_start
    out += b"HDWC"
    out += struct.pack("<I", 8 + cwdh_data_size)
    out += struct.pack("<H", 0)
    out += struct.pack("<H", 1)
    out += struct.pack("<I", 0)
    out += struct.pack("<bBb", 0, CELL_WIDTH, CELL_WIDTH)
    out += struct.pack("<bBb", 0, CELL_WIDTH, CELL_WIDTH)

    assert len(out) == cmap_start
    out += b"PAMC"
    out += struct.pack("<I", 8 + cmap_data_size)
    out += struct.pack("<H", CODEPOINT_A)
    out += struct.pack("<H", CODEPOINT_A)
    out += struct.pack("<H", 1)
    out += struct.pack("<H", 0)
    out += struct.pack("<I", 0)
    out += struct.pack("<H", GLYPH_INDEX_A)

    assert len(out) == total
    return bytes(out)
