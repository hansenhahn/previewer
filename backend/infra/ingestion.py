import io
import zipfile
from pathlib import PurePosixPath

from sqlalchemy.exc import IntegrityError

from domain.project import parse_manifest

MANIFEST_NAME = "manifest.json"


class IngestionError(RuntimeError):
    pass


class InvalidBundleError(IngestionError):
    pass


class ProjectNameConflict(IngestionError):
    pass


def _is_unsafe(name: str) -> bool:
    path = PurePosixPath(name)
    return (
        not name
        or path.is_absolute()
        or ".." in path.parts
        or "\\" in name
        or "\x00" in name
        or (len(name) > 1 and name[1] == ":")
    )


def _validate_members(names) -> None:
    for name in names:
        if _is_unsafe(name):
            raise InvalidBundleError(f"membro com caminho inválido: {name!r}")


def import_bundle(*, storage, repository, owner_id: str, data: bytes):
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as exc:
        raise InvalidBundleError("bundle não é um zip válido") from exc

    names = archive.namelist()
    _validate_members(names)

    if MANIFEST_NAME not in names:
        raise InvalidBundleError("manifesto ausente no bundle")

    manifest = parse_manifest(archive.read(MANIFEST_NAME))

    for asset in (*manifest.fonts, *manifest.backgrounds):
        if asset.path not in names:
            raise InvalidBundleError(f"arquivo referenciado ausente: {asset.path}")

    try:
        project = repository.create(owner_id, manifest.name, manifest.encoding)
    except IntegrityError as exc:
        raise ProjectNameConflict(
            f"já existe um projeto chamado {manifest.name!r}"
        ) from exc

    project_id = str(project.id)
    written = []
    try:
        storage.create_project(owner_id, project_id)
        for name in names:
            if name.endswith("/"):
                continue
            storage.write_file(owner_id, project_id, name, archive.read(name))
            written.append(name)
    except Exception:
        for name in written:
            try:
                storage.delete_file(owner_id, project_id, name)
            except Exception:
                pass
        repository.delete(project.id)
        raise

    return project, manifest
