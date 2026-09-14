import json

import pytest

from domain.project import ManifestError, ProjectManifest, parse_manifest


def dump(document) -> bytes:
    return json.dumps(document).encode("utf-8")


def valid_document() -> dict:
    return {
        "format": "previewer-project",
        "version": 1,
        "name": "Meu Projeto",
        "encoding": "windows-1252",
        "texts": {"source": "texts", "original": "original"},
        "fonts": [{"name": "fontevent", "path": "fonts/fontevent.NFTR"}],
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
        "tags": ["<tag>"],
        "matches": ["#"],
    }


def test_parses_valid_manifest():
    manifest = parse_manifest(dump(valid_document()))
    assert isinstance(manifest, ProjectManifest)
    assert manifest.name == "Meu Projeto"
    assert manifest.encoding == "windows-1252"
    assert manifest.texts.source == "texts"
    assert manifest.font("fontevent").path == "fonts/fontevent.NFTR"
    assert manifest.background("bg1").path == "backgrounds/bg1.png"
    assert manifest.screens[0].new_line == 12
    assert manifest.tags == ("<tag>",)
    assert manifest.matches == ("#",)


def test_parses_minimal_manifest():
    document = {
        "format": "previewer-project",
        "version": 1,
        "name": "Min",
        "encoding": "utf-8",
        "texts": {"source": "texts"},
    }
    manifest = parse_manifest(dump(document))
    assert manifest.fonts == ()
    assert manifest.screens == ()
    assert manifest.texts.original is None


def test_rejects_malformed_json():
    with pytest.raises(ManifestError):
        parse_manifest(b"{ not json")


def test_rejects_unknown_format():
    document = valid_document()
    document["format"] = "outra-coisa"
    with pytest.raises(ManifestError):
        parse_manifest(dump(document))


def test_rejects_unsupported_version():
    document = valid_document()
    document["version"] = 99
    with pytest.raises(ManifestError):
        parse_manifest(dump(document))


@pytest.mark.parametrize("field", ["name", "encoding"])
def test_rejects_missing_required_field(field):
    document = valid_document()
    del document[field]
    with pytest.raises(ManifestError):
        parse_manifest(dump(document))


def test_rejects_missing_texts():
    document = valid_document()
    del document["texts"]
    with pytest.raises(ManifestError):
        parse_manifest(dump(document))


def test_rejects_screen_unknown_font():
    document = valid_document()
    document["screens"][0]["font"] = "nao-existe"
    with pytest.raises(ManifestError):
        parse_manifest(dump(document))


def test_rejects_screen_unknown_background():
    document = valid_document()
    document["screens"][0]["background"] = "nao-existe"
    with pytest.raises(ManifestError):
        parse_manifest(dump(document))


def test_rejects_invalid_screen_coordinate():
    document = valid_document()
    document["screens"][0]["x"] = "oito"
    with pytest.raises(ManifestError):
        parse_manifest(dump(document))


def test_parses_segments():
    document = valid_document()
    document["segments"] = {
        "start": ["^<d>"],
        "end": ["^</d>"],
        "separators": ["^!.*!$"],
    }
    manifest = parse_manifest(dump(document))
    assert manifest.segments.start == ("^<d>",)
    assert manifest.segments.end == ("^</d>",)
    assert manifest.segments.separators == ("^!.*!$",)


def test_segments_absent_is_none():
    assert parse_manifest(dump(valid_document())).segments is None


def test_rejects_invalid_segments():
    document = valid_document()
    document["segments"] = ["nope"]
    with pytest.raises(ManifestError):
        parse_manifest(dump(document))
