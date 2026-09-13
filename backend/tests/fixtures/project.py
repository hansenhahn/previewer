import io
import json
import zipfile
from pathlib import Path

FONT_FIXTURE = Path(__file__).resolve().parent / "fonts" / "fontevent.NFTR"


def manifest_document(name="Meu Projeto", font_path="fonts/fontevent.NFTR"):
    return {
        "format": "previewer-project",
        "version": 1,
        "name": name,
        "encoding": "windows-1252",
        "texts": {"source": "texts", "original": "original"},
        "fonts": [{"name": "fontevent", "path": font_path}],
        "backgrounds": [{"name": "bg1", "path": "backgrounds/bg1.png"}],
        "screens": [
            {
                "name": "default",
                "font": "fontevent",
                "background": "bg1",
                "x": 8,
                "y": 16,
                "new_line": 12,
            }
        ],
    }


def build_bundle(document=None, extra_members=None, font_bytes=None):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("manifest.json", json.dumps(document or manifest_document()))
        archive.writestr("texts/cap01.txt", b"texto")
        archive.writestr("original/cap01.txt", b"original")
        archive.writestr(
            "fonts/fontevent.NFTR", font_bytes or FONT_FIXTURE.read_bytes()
        )
        archive.writestr("backgrounds/bg1.png", b"\x89PNG\r\n")
        for name, content in (extra_members or {}).items():
            archive.writestr(name, content)
    return buffer.getvalue()
