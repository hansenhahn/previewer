import mimetypes
import uuid

from flask import Blueprint, current_app, jsonify, request, url_for

from domain.errors import FontDecodeError, UnsupportedFontError
from domain.project import ManifestError, parse_manifest
from domain.text import decode_text, encode_text
from infra.atlas import generate as generate_atlas
from infra.ingestion import InvalidBundleError, ProjectNameConflict, import_bundle
from infra.storage import PathTraversalError

DEFAULT_OWNER = "local"
MANIFEST_NAME = "manifest.json"

bp = Blueprint("api", __name__, url_prefix="/api")


class ApiError(Exception):
    status = 400
    code = "error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(ApiError):
    status = 404
    code = "not_found"


@bp.errorhandler(ApiError)
def _handle_api_error(error):
    return jsonify(error={"code": error.code, "message": error.message}), error.status


@bp.errorhandler(ManifestError)
def _handle_manifest(error):
    return jsonify(error={"code": "invalid_manifest", "message": str(error)}), 400


@bp.errorhandler(InvalidBundleError)
def _handle_bundle(error):
    return jsonify(error={"code": "invalid_bundle", "message": str(error)}), 400


@bp.errorhandler(ProjectNameConflict)
def _handle_conflict(error):
    return jsonify(error={"code": "conflict", "message": str(error)}), 409


@bp.errorhandler(UnsupportedFontError)
@bp.errorhandler(FontDecodeError)
def _handle_font(error):
    return jsonify(error={"code": "unsupported_font", "message": str(error)}), 422


@bp.errorhandler(PathTraversalError)
def _handle_path(error):
    return jsonify(error={"code": "invalid_path", "message": str(error)}), 400


@bp.errorhandler(FileNotFoundError)
def _handle_not_found(error):
    return jsonify(error={"code": "not_found", "message": "recurso não encontrado"}), 404


def _owner() -> str:
    return DEFAULT_OWNER


def _storage():
    return current_app.extensions["storage"]


def _projects():
    return current_app.extensions["projects"]


def _project(project_id: str):
    try:
        key = uuid.UUID(project_id)
    except (ValueError, AttributeError, TypeError):
        raise NotFoundError("projeto não encontrado")
    project = _projects().get(key)
    if project is None:
        raise NotFoundError("projeto não encontrado")
    return project


def _manifest(project):
    data = _storage().read_file(_owner(), str(project.id), MANIFEST_NAME)
    return parse_manifest(data)


def _project_dict(project) -> dict:
    return {
        "id": str(project.id),
        "name": project.name,
        "encoding": project.encoding,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
    }


def _font_asset(project, name):
    manifest = _manifest(project)
    asset = manifest.font(name)
    if asset is None:
        raise NotFoundError("fonte não encontrada")
    return manifest, asset


@bp.get("/projects")
def list_projects():
    projects = _projects().list_for_owner(_owner())
    return jsonify(projects=[_project_dict(project) for project in projects])


@bp.post("/projects")
def create_project():
    upload = request.files.get("file")
    if upload is None:
        raise InvalidBundleError("arquivo do bundle ausente (campo 'file')")
    project, _ = import_bundle(
        storage=_storage(),
        repository=_projects(),
        owner_id=_owner(),
        data=upload.read(),
    )
    return jsonify(_project_dict(project)), 201


@bp.get("/projects/<project_id>")
def get_project(project_id):
    project = _project(project_id)
    payload = _project_dict(project)
    payload["manifest"] = _manifest(project).to_dict()
    return jsonify(payload)


@bp.get("/projects/<project_id>/files")
def list_files(project_id):
    project = _project(project_id)
    manifest = _manifest(project)
    prefix = manifest.texts.source.rstrip("/") + "/"
    files = [
        path
        for path in _storage().list_files(_owner(), str(project.id))
        if path.startswith(prefix)
    ]
    return jsonify(files=files)


def _original_path(manifest, relpath: str) -> str:
    original_root = manifest.texts.original
    if not original_root:
        raise NotFoundError("projeto não possui texto original")
    prefix = manifest.texts.source.rstrip("/") + "/"
    if not relpath.startswith(prefix):
        raise NotFoundError("arquivo não encontrado")
    return original_root.rstrip("/") + "/" + relpath[len(prefix):]


@bp.get("/projects/<project_id>/files/<path:relpath>")
def read_file(project_id, relpath):
    project = _project(project_id)
    manifest = _manifest(project)
    variant = request.args.get("variant", "source")
    if variant == "original":
        target = _original_path(manifest, relpath)
    elif variant == "source":
        target = relpath
    else:
        raise ApiError("variante inválida")
    data = _storage().read_file(_owner(), str(project.id), target)
    return jsonify(
        path=relpath,
        content=decode_text(data, manifest.encoding),
        encoding=manifest.encoding,
        variant=variant,
    )


@bp.put("/projects/<project_id>/files/<path:relpath>")
def write_file(project_id, relpath):
    project = _project(project_id)
    manifest = _manifest(project)
    body = request.get_json(silent=True) or {}
    content = body.get("content")
    if not isinstance(content, str):
        raise ApiError("campo 'content' ausente ou inválido")
    _storage().write_file(
        _owner(), str(project.id), relpath, encode_text(content, manifest.encoding)
    )
    return jsonify(path=relpath, encoding=manifest.encoding)


@bp.get("/projects/<project_id>/fonts/<name>/atlas")
def font_atlas(project_id, name):
    project = _project(project_id)
    _, asset = _font_asset(project, name)
    font_bytes = _storage().read_file(_owner(), str(project.id), asset.path)
    _, metrics = generate_atlas(font_bytes)
    metrics["image"]["url"] = url_for(
        "api.font_atlas_png", project_id=project_id, name=name
    )
    return jsonify(metrics)


@bp.get("/projects/<project_id>/fonts/<name>/atlas.png")
def font_atlas_png(project_id, name):
    project = _project(project_id)
    _, asset = _font_asset(project, name)
    font_bytes = _storage().read_file(_owner(), str(project.id), asset.path)
    png, _ = generate_atlas(font_bytes)
    return current_app.response_class(png, mimetype="image/png")


@bp.get("/projects/<project_id>/backgrounds/<name>")
def project_background(project_id, name):
    project = _project(project_id)
    manifest = _manifest(project)
    asset = manifest.background(name)
    if asset is None:
        raise NotFoundError("ativo não encontrado")
    data = _storage().read_file(_owner(), str(project.id), asset.path)
    mimetype = mimetypes.guess_type(asset.path)[0] or "application/octet-stream"
    return current_app.response_class(data, mimetype=mimetype)
