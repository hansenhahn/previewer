import json
from dataclasses import dataclass

FORMAT = "previewer-project"
SUPPORTED_VERSIONS = (1,)


class ManifestError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Asset:
    name: str
    path: str


@dataclass(frozen=True, slots=True)
class Screen:
    name: str
    font: str
    background: str
    x: int
    y: int
    new_line: int


@dataclass(frozen=True, slots=True)
class Texts:
    source: str
    original: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectManifest:
    name: str
    encoding: str
    texts: Texts
    fonts: tuple[Asset, ...] = ()
    backgrounds: tuple[Asset, ...] = ()
    screens: tuple[Screen, ...] = ()
    tags: tuple[str, ...] = ()
    matches: tuple[str, ...] = ()
    version: int = 1
    format: str = FORMAT

    def font(self, name: str) -> Asset | None:
        return _find(self.fonts, name)

    def background(self, name: str) -> Asset | None:
        return _find(self.backgrounds, name)

    def to_dict(self) -> dict:
        return {
            "format": self.format,
            "version": self.version,
            "name": self.name,
            "encoding": self.encoding,
            "texts": {
                "source": self.texts.source,
                "original": self.texts.original,
            },
            "fonts": [{"name": a.name, "path": a.path} for a in self.fonts],
            "backgrounds": [{"name": a.name, "path": a.path} for a in self.backgrounds],
            "screens": [
                {
                    "name": s.name,
                    "font": s.font,
                    "background": s.background,
                    "x": s.x,
                    "y": s.y,
                    "new_line": s.new_line,
                }
                for s in self.screens
            ],
            "tags": list(self.tags),
            "matches": list(self.matches),
        }


def _find(assets: tuple[Asset, ...], name: str) -> Asset | None:
    for asset in assets:
        if asset.name == name:
            return asset
    return None


def _require_text(mapping: dict, key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"campo obrigatório inválido: {key}")
    return value


def _string_list(mapping: dict, key: str) -> tuple[str, ...]:
    value = mapping.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ManifestError(f"campo inválido: {key} deve ser uma lista de strings")
    return tuple(value)


def _assets(mapping: dict, key: str) -> tuple[Asset, ...]:
    value = mapping.get(key, [])
    if not isinstance(value, list):
        raise ManifestError(f"campo inválido: {key} deve ser uma lista")
    assets = []
    for item in value:
        if not isinstance(item, dict):
            raise ManifestError(f"item inválido em {key}")
        assets.append(Asset(_require_text(item, "name"), _require_text(item, "path")))
    return tuple(assets)


def _screens(mapping: dict) -> tuple[Screen, ...]:
    value = mapping.get("screens", [])
    if not isinstance(value, list):
        raise ManifestError("campo inválido: screens deve ser uma lista")
    screens = []
    for item in value:
        if not isinstance(item, dict):
            raise ManifestError("item inválido em screens")
        for field in ("x", "y", "new_line"):
            if not isinstance(item.get(field), int) or isinstance(item.get(field), bool):
                raise ManifestError(f"campo inválido em screens: {field}")
        screens.append(
            Screen(
                name=_require_text(item, "name"),
                font=_require_text(item, "font"),
                background=_require_text(item, "background"),
                x=item["x"],
                y=item["y"],
                new_line=item["new_line"],
            )
        )
    return tuple(screens)


def parse_manifest(data: bytes) -> ProjectManifest:
    try:
        document = json.loads(data)
    except (ValueError, TypeError) as exc:
        raise ManifestError("manifesto inválido: JSON malformado") from exc
    if not isinstance(document, dict):
        raise ManifestError("manifesto inválido: esperado um objeto JSON")

    if document.get("format") != FORMAT:
        raise ManifestError("formato de manifesto não reconhecido")

    version = document.get("version")
    if version not in SUPPORTED_VERSIONS:
        raise ManifestError(f"versão de manifesto não suportada: {version!r}")

    name = _require_text(document, "name")
    encoding = _require_text(document, "encoding")

    texts_raw = document.get("texts")
    if not isinstance(texts_raw, dict):
        raise ManifestError("campo obrigatório inválido: texts")
    texts = Texts(
        source=_require_text(texts_raw, "source"),
        original=texts_raw.get("original"),
    )

    fonts = _assets(document, "fonts")
    backgrounds = _assets(document, "backgrounds")
    screens = _screens(document)

    for screen in screens:
        if _find(fonts, screen.font) is None:
            raise ManifestError(
                f"tela {screen.name!r} referencia fonte desconhecida: {screen.font!r}"
            )
        if _find(backgrounds, screen.background) is None:
            raise ManifestError(
                f"tela {screen.name!r} referencia background desconhecido: "
                f"{screen.background!r}"
            )

    return ProjectManifest(
        name=name,
        encoding=encoding,
        texts=texts,
        fonts=fonts,
        backgrounds=backgrounds,
        screens=screens,
        tags=_string_list(document, "tags"),
        matches=_string_list(document, "matches"),
        version=version,
        format=FORMAT,
    )
