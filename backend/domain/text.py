from .errors import TextDecodeError, TextEncodeError


def decode_text(data: bytes, encoding: str) -> str:
    try:
        text = data.decode(encoding)
    except (UnicodeDecodeError, LookupError) as exc:
        raise TextDecodeError(f"não foi possível decodificar usando {encoding!r}") from exc
    return text.replace("\r\n", "\n").replace("\r", "\n")


def encode_text(text: str, encoding: str) -> bytes:
    try:
        return text.encode(encoding)
    except (UnicodeEncodeError, LookupError) as exc:
        raise TextEncodeError(f"não foi possível codificar usando {encoding!r}") from exc
