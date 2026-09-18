import struct

from .base import Glyph
from ..errors import FontDecodeError, UnsupportedFontError

MAGIC = b"NFTR"
_FINF_MAGIC = b"FINF"
_CGLP_MAGIC = b"CGLP"
_CWDH_MAGIC = b"CWDH"
_CMAP_MAGIC = b"CMAP"

_NFTR_HEADER_SIZE = 16
_BLOCK_HEADER_SIZE = 8
_CGLP_HEADER_SIZE = 8
_CWDH_HEADER_SIZE = 8
_CWDH_ENTRY_SIZE = 3
_CMAP_HEADER_SIZE = 12
_UNMAPPED = 0xFFFF


def _tag(data: bytes, offset: int) -> bytes:
    # As assinaturas do formato NNS G2D são tags u32 em little-endian, então os
    # 4 bytes aparecem invertidos no arquivo ("RTFN" para a tag "NFTR").
    end = offset + 4
    if offset < 0 or end > len(data):
        raise FontDecodeError("arquivo NFTR truncado")
    return data[offset:end][::-1]


def _unpack(fmt: str, data: bytes, offset: int):
    size = struct.calcsize(fmt)
    if offset < 0 or offset + size > len(data):
        raise FontDecodeError("arquivo NFTR truncado")
    return struct.unpack_from(fmt, data, offset)


def _u8(data: bytes, offset: int) -> int:
    return _unpack("<B", data, offset)[0]


def _s8(data: bytes, offset: int) -> int:
    return _unpack("<b", data, offset)[0]


def _u16(data: bytes, offset: int) -> int:
    return _unpack("<H", data, offset)[0]


def _u32(data: bytes, offset: int) -> int:
    return _unpack("<I", data, offset)[0]


class NftrFont:
    def __init__(self, data: bytes):
        self._source = data
        self._parse()

    def _parse(self) -> None:
        data = self._source
        if len(data) < _NFTR_HEADER_SIZE or _tag(data, 0) != MAGIC:
            raise FontDecodeError("assinatura NFTR ausente")
        if _tag(data, 16) != _FINF_MAGIC:
            raise FontDecodeError("bloco FINF ausente")

        finf = _NFTR_HEADER_SIZE
        self.font_type = _u8(data, finf + 8)
        self.line_height = _u8(data, finf + 9)
        self.invalid_glyph_index = _u16(data, finf + 10)
        self.default_leading = _s8(data, finf + 12)
        self.default_width = _u8(data, finf + 13)
        self.default_trailing = _s8(data, finf + 14)
        self.encoding = _u8(data, finf + 15)
        cglp_offset = _u32(data, finf + 16)
        cwdh_offset = _u32(data, finf + 20)
        cmap_offset = _u32(data, finf + 24)
        self.default_advance = (
            self.default_leading + self.default_width + self.default_trailing
        )

        self.cell_width, self.cell_height, self.bpp, buffers = self._read_cglp(
            cglp_offset
        )
        self.widths = self._read_cwdh(cwdh_offset)
        self.cmap = self._read_cmap(cmap_offset)

        self.glyphs = []
        for index, (pixels, width, height) in enumerate(buffers):
            advance, leading = self.widths.get(
                index, (self.default_advance, self.default_leading)
            )
            self.glyphs.append(Glyph(index, pixels, width, height, advance, leading))

    def _read_cglp(self, offset: int):
        data = self._source
        start = offset - _BLOCK_HEADER_SIZE
        if start < 0 or _tag(data, start) != _CGLP_MAGIC:
            raise FontDecodeError("bloco CGLP ausente")
        block_size = _u32(data, start + 4)
        width = _u8(data, offset)
        height = _u8(data, offset + 1)
        cell_size = _u16(data, offset + 2)
        bpp = _u8(data, offset + 6)
        if bpp != 1:
            raise UnsupportedFontError(f"NFTR de {bpp} bpp não suportado")
        if cell_size == 0:
            raise FontDecodeError("tamanho de célula inválido")

        # O tamanho do bloco G2D inclui o header de bloco (8) e o header do CGLP (8).
        count = (block_size - _BLOCK_HEADER_SIZE - _CGLP_HEADER_SIZE) // cell_size
        if count < 0:
            raise FontDecodeError("bloco CGLP inconsistente")
        glyphs_start = offset + _CGLP_HEADER_SIZE
        if glyphs_start + count * cell_size > len(data):
            raise FontDecodeError("dados de glifos truncados")

        buffers = []
        for i in range(count):
            raw = data[glyphs_start + i * cell_size : glyphs_start + (i + 1) * cell_size]
            buffers.append(self._build_bitmap(raw, width, height))
        return width, height, bpp, buffers

    def _build_bitmap(self, raw: bytes, width: int, height: int):
        required = (width * height + 7) // 8
        if len(raw) < required:
            raise FontDecodeError("dados de glifo truncados")

        bits = []
        for byte in raw:
            for shift in range(7, -1, -1):
                bits.append(1 if byte & (1 << shift) else 0)

        padded_width = ((width + 7) // 8) * 8
        pixels = bytearray()
        position = 0
        for _ in range(height):
            for _ in range(width):
                pixels.append(255 if bits[position] else 0)
                position += 1
            pixels.extend(b"\x00" * (padded_width - width))
        return bytes(pixels), padded_width, height

    def _read_cwdh(self, offset: int):
        data = self._source
        start = offset - _BLOCK_HEADER_SIZE
        if start < 0 or _tag(data, start) != _CWDH_MAGIC:
            raise FontDecodeError("bloco CWDH ausente")
        first = _u16(data, offset)
        last = _u16(data, offset + 2)
        count = last - first + 1
        entries_start = offset + _CWDH_HEADER_SIZE
        if count < 0 or entries_start + count * _CWDH_ENTRY_SIZE > len(data):
            raise FontDecodeError("tabela CWDH truncada")

        widths = {}
        for i in range(count):
            base = entries_start + i * _CWDH_ENTRY_SIZE
            leading = _s8(data, base)
            total = _s8(data, base + 2)
            widths[first + i] = (total, leading)
        return widths

    def _read_cmap(self, offset: int):
        data = self._source
        cmap = {}
        visited = set()
        # O CMAP pode ser uma cadeia de segmentos: os 4 bytes em offset+8
        # apontam para o proximo segmento (0 = fim). Fontes com um unico
        # segmento (ex.: playton-3) tem next=0 e caem no caso trivial.
        while offset:
            if offset in visited:
                break
            visited.add(offset)
            start = offset - _BLOCK_HEADER_SIZE
            if start < 0 or _tag(data, start) != _CMAP_MAGIC:
                raise FontDecodeError("bloco CMAP ausente")
            first = _u16(data, offset)
            last = _u16(data, offset + 2)
            mapping_type = _u16(data, offset + 4)
            next_offset = _u32(data, offset + 8)
            mapping = offset + _CMAP_HEADER_SIZE
            count = last - first + 1
            if count < 0:
                raise FontDecodeError("faixa de CMAP invalida")

            if mapping_type == 0:
                first_index = _u16(data, mapping)
                for i in range(count):
                    cmap[first + i] = first_index + i
            elif mapping_type == 1:
                if mapping + count * 2 > len(data):
                    raise FontDecodeError("tabela CMAP truncada")
                for i in range(count):
                    index = _u16(data, mapping + i * 2)
                    if index != _UNMAPPED:
                        cmap[first + i] = index
            elif mapping_type == 2:
                entries = _u16(data, mapping)
                base = mapping + 2
                if base + entries * 4 > len(data):
                    raise FontDecodeError("tabela CMAP truncada")
                for i in range(entries):
                    codepoint = _u16(data, base + i * 4)
                    index = _u16(data, base + i * 4 + 2)
                    if index != _UNMAPPED:
                        cmap[codepoint] = index
            else:
                raise FontDecodeError("tipo de CMAP desconhecido")

            offset = next_offset
        return cmap

    def _blank_glyph(self) -> Glyph:
        padded_width = ((self.cell_width + 7) // 8) * 8
        pixels = bytes(padded_width * self.cell_height)
        return Glyph(
            -1, pixels, padded_width, self.cell_height, self.default_advance,
            self.default_leading,
        )

    def _invalid_glyph(self) -> Glyph:
        index = self.invalid_glyph_index
        if 0 <= index < len(self.glyphs):
            base = self.glyphs[index]
            return Glyph(
                base.index, base.pixels, base.width, base.height,
                self.default_advance, base.leading,
            )
        return self._blank_glyph()

    def glyph(self, codepoint: int, size: int | None = None) -> Glyph | None:
        index = self.cmap.get(codepoint)
        if index is None or not (0 <= index < len(self.glyphs)):
            return self._invalid_glyph()
        return self.glyphs[index]

    def advance(self, codepoint: int) -> int:
        glyph = self.glyph(codepoint)
        if glyph is None:
            return self.default_advance
        return glyph.advance


class NftrFontFormat:
    name = "nftr"

    def sniff(self, data: bytes) -> bool:
        return data[0:4] == MAGIC[::-1]

    def load(self, data: bytes) -> NftrFont:
        return NftrFont(data)
