import pytest

from domain.errors import TextDecodeError
from domain.text import decode_text, encode_text


def test_decode_crlf_normalizes():
    assert decode_text(b"a\r\nb\rc\nd", "windows-1252") == "a\nb\nc\nd"


def test_decode_uses_project_encoding():
    assert decode_text("ação".encode("windows-1252"), "windows-1252") == "ação"


def test_decode_invalid_bytes_raises():
    with pytest.raises(TextDecodeError):
        decode_text(b"\xff\xfe\x00", "ascii")


def test_encode_roundtrip():
    text = "Olá, mundo!\nSegunda linha"
    data = encode_text(text, "windows-1252")
    assert decode_text(data, "windows-1252") == text
