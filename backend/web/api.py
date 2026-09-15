import mimetypes
import re
import time
import unicodedata
import uuid

from flask import Blueprint, current_app, jsonify, request, url_for

from domain.errors import FontDecodeError, UnsupportedFontError
from domain.project import ManifestError, parse_manifest
from domain.text import decode_text, encode_text
from infra.atlas import generate as generate_atlas
from infra.git import GitError
from infra.github_export import GitHubExportError
from infra.github_import import refresh_repositories
from infra.github_source import GitHubSourceError, import_repository
from infra.identity import IdentityError
from infra.ingestion import InvalidBundleError, ProjectNameConflict, import_bundle
from infra.project_export import (
    EPHEMERAL_BRANCH,
    ProjectExportError,
    backup_branch,
)
from infra.storage import PathTraversalError
from .auth import current_user

MANIFEST_NAME = "manifest.json"

bp = Blueprint("api", __name__, url_prefix="/api")

_CACHE: dict = {}


def _cached(key, ttl: float, producer):
    now = time.monotonic()
    hit = _CACHE.get(key)
    if hit is not None and now - hit[0] < ttl:
        return hit[1]
    value = producer()
    _CACHE[key] = (now, value)
    return value


@bp.before_request
def _require_authentication():
    if current_user() is None:
        return (
            jsonify(error={"code": "unauthorized", "message": "autenticação necessária"}),
            401,
        )


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


@bp.errorhandler(GitHubSourceError)
def _handle_github(error):
    return jsonify(error={"code": "github_error", "message": str(error)}), 422


@bp.errorhandler(IdentityError)
@bp.errorhandler(GitHubExportError)
def _handle_identity(error):
    return jsonify(error={"code": "github_error", "message": str(error)}), 422


@bp.errorhandler(GitError)
def _handle_git(error):
    return jsonify(error={"code": "git_error", "message": str(error)}), 422


@bp.errorhandler(ProjectExportError)
def _handle_export(error):
    return (
        jsonify(error={"code": "pending_changes", "message": str(error)}),
        409,
    )


@bp.errorhandler(FileNotFoundError)
def _handle_not_found(error):
    return jsonify(error={"code": "not_found", "message": "recurso não encontrado"}), 404


def _owner() -> str:
    return str(current_user().id)


def _storage():
    return current_app.extensions["storage"]


def _projects():
    return current_app.extensions["projects"]


def _repositories():
    return current_app.extensions.get("repositories")


def _users():
    return current_app.extensions.get("users")


def _changes():
    return current_app.extensions.get("changes")


def _export():
    return current_app.extensions["project_export"]


def _workspace(project):
    return _storage().local_path(_owner(), str(project.id))


def _is_git(workspace) -> bool:
    return (workspace / ".git").exists()


def _base(project) -> str:
    if project.base_branch:
        return project.base_branch
    return _export().default_branch(workspace=_workspace(project))


def _upstream(project) -> str | None:
    if project.upstream:
        return project.upstream
    return _export().origin_remote(workspace=_workspace(project))


def _head_repo(project) -> str | None:
    return _export().origin_remote(workspace=_workspace(project))


def _token():
    return _users().access_token_for(current_user().id)


def _login() -> str:
    identity = _users().identity_for(current_user().id)
    return identity.login if identity else ""


def _slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug or "alteracao"


def _change_dict(change) -> dict:
    return {
        "id": str(change.id),
        "branch": change.branch,
        "title": change.title,
        "pr_number": change.pr_number,
        "status": change.status,
        "updated_at": change.updated_at.isoformat(),
    }


def _active_change(project):
    workspace = _workspace(project)
    branch = _export().current_branch(workspace=workspace)
    change = _changes().find(project.id, current_user().id, branch)
    return workspace, branch, change


def _unique_branch(project, workspace, slug: str) -> str:
    export = _export()
    changes = _changes()
    candidate = f"previewer/{slug}"
    index = 2
    while export.branch_exists(workspace=workspace, branch=candidate) or changes.find(
        project.id, current_user().id, candidate
    ):
        candidate = f"previewer/{slug}-{index}"
        index += 1
    return candidate


def _ensure_draft(project, relpath: str | None = None):
    workspace, _, change = _active_change(project)
    if change is not None:
        return workspace, change
    export = _export()
    base = _base(project)
    export.ensure_branch(workspace=workspace, branch=EPHEMERAL_BRANCH, base=base)
    existing = _changes().find(project.id, current_user().id, EPHEMERAL_BRANCH)
    if existing is not None:
        return workspace, existing
    change = _changes().create(project.id, current_user().id, EPHEMERAL_BRANCH)
    return workspace, change


def _change_or_404(project, change_id: str):
    try:
        key = uuid.UUID(change_id)
    except (ValueError, AttributeError, TypeError):
        raise NotFoundError("alteração não encontrada")
    change = _changes().get(key)
    if (
        change is None
        or change.project_id != project.id
        or change.user_id != current_user().id
    ):
        raise NotFoundError("alteração não encontrada")
    return change


def _refresh_status(change, project):
    if not change.pr_number:
        return change
    export = _export()
    upstream = _upstream(project)
    token = _token()
    if not upstream or not token:
        return change
    try:
        state = _cached(
            ("pr", upstream, change.pr_number),
            120,
            lambda: export.pr_status(
                upstream=upstream, number=change.pr_number, token=token
            ),
        )
    except Exception:
        return change
    status = state.state
    if status != change.status:
        change = _changes().update(change.id, status=status)
    return change


def _project(project_id: str):
    try:
        key = uuid.UUID(project_id)
    except (ValueError, AttributeError, TypeError):
        raise NotFoundError("projeto não encontrado")
    project = _projects().get(key)
    if project is None or project.owner_id != _owner():
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
        "upstream": project.upstream,
        "base_branch": project.base_branch,
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


def _repository_dict(repo) -> dict:
    return {
        "provider": repo.provider,
        "full_name": repo.full_name,
        "default_branch": repo.default_branch,
        "fork": repo.fork,
        "manifest_ok": repo.manifest_ok,
        "manifest_error": repo.manifest_error,
    }


@bp.get("/github/repos")
def list_github_repos():
    store = _repositories()
    repos = store.list_for_user(current_user().id) if store is not None else []
    return jsonify(repositories=[_repository_dict(repo) for repo in repos])


@bp.post("/github/repos/refresh")
def refresh_github_repos():
    user = current_user()
    store = _repositories()
    if store is None:
        return jsonify(repositories=[])
    token = _users().access_token_for(user.id)
    if not token:
        raise GitHubSourceError("sem token do provedor; faça login novamente")
    repos = refresh_repositories(
        store=store,
        provider=current_app.extensions["identity_provider"],
        user_id=user.id,
        token=token,
    )
    return jsonify(repositories=[_repository_dict(repo) for repo in repos])


def _resolve_upstream(record) -> tuple[str, str]:
    provider = current_app.extensions.get("identity_provider")
    token = _token()
    if provider is None or not hasattr(provider, "get_repo") or not token:
        return record.full_name, record.default_branch
    try:
        meta = provider.get_repo(record.full_name, token)
    except IdentityError:
        return record.full_name, record.default_branch
    parent = meta.get("parent") or {}
    return (
        parent.get("full_name") or record.full_name,
        parent.get("default_branch") or record.default_branch,
    )


@bp.post("/projects/github")
def import_github_project():
    body = request.get_json(silent=True) or {}
    full_name = body.get("full_name")
    if not isinstance(full_name, str) or not full_name.strip():
        raise ApiError("campo 'full_name' ausente ou inválido")
    full_name = full_name.strip()
    store = _repositories()
    record = store.find(current_user().id, full_name) if store is not None else None
    if record is None:
        raise NotFoundError("repositório não encontrado na conta")
    if not record.manifest_ok:
        raise GitHubSourceError("repositório não possui manifest.json válido")
    upstream, base_branch = _resolve_upstream(record)
    project, _ = import_repository(
        storage=_storage(),
        repository=_projects(),
        source=current_app.extensions["github_source"],
        owner_id=_owner(),
        full_name=record.full_name,
        default_branch=record.default_branch,
        upstream=upstream,
        base_branch=base_branch,
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
    payload = {"path": relpath, "encoding": manifest.encoding}
    workspace = _workspace(project)
    if _is_git(workspace):
        export = _export()
        workspace, change = _ensure_draft(project, relpath)
        export.commit(
            workspace=workspace,
            branch=change.branch,
            base=_base(project),
            message=change.title or "rascunho",
        )
        payload["change"] = _change_dict(change)
    return jsonify(payload)


def _sync_open_pulls(project) -> dict[str, bool]:
    workspace = _workspace(project)
    if not _is_git(workspace):
        return {}
    upstream = _upstream(project)
    head = _head_repo(project)
    token = _token()
    if not upstream or not head or not token:
        return {}
    key = ("pulls", str(project.id), str(current_user().id))
    return _cached(
        key, 60, lambda: _fetch_open_pulls(project, upstream, head, token)
    )


def _fetch_open_pulls(project, upstream, head, token) -> dict[str, bool]:
    try:
        pulls = _export().open_pulls(
            upstream=upstream, head_repo=head, token=token
        )
    except Exception:
        return {}
    changes = _changes()
    resumable: dict[str, bool] = {}
    for pull in pulls:
        resumable[pull.branch] = pull.resumable
        existing = changes.find(project.id, current_user().id, pull.branch)
        if existing is None:
            changes.create(
                project.id,
                current_user().id,
                pull.branch,
                title=pull.title,
                status="open",
                pr_number=pull.number,
            )
        elif (
            existing.pr_number != pull.number
            or existing.status != "open"
            or existing.title != pull.title
        ):
            changes.update(
                existing.id,
                title=pull.title,
                pr_number=pull.number,
                status="open",
            )
    return resumable


@bp.get("/projects/<project_id>/changes")
def list_changes(project_id):
    project = _project(project_id)
    sync = request.args.get("sync") in ("1", "true")
    resumable = _sync_open_pulls(project) if sync else {}
    rows = _changes().list_for_user(current_user().id, project.id)
    changes = []
    for change in rows:
        item = _change_dict(change)
        item["resumable"] = resumable.get(change.branch, True)
        changes.append(item)
    return jsonify(changes=changes)


@bp.get("/projects/<project_id>/changes/state")
def change_state(project_id):
    project = _project(project_id)
    workspace = _workspace(project)
    if not _is_git(workspace):
        return jsonify(branch=None, status="base", change=None, can_publish=False)
    export = _export()
    branch = export.current_branch(workspace=workspace)
    base = _base(project)
    change = _changes().find(project.id, current_user().id, branch)
    if change is None:
        return jsonify(branch=branch, status="base", change=None, can_publish=False)
    change = _refresh_status(change, project)
    can_publish = export.has_unpushed(
        workspace=workspace, branch=branch, base=base
    )
    return jsonify(
        branch=branch,
        status=change.status,
        change=_change_dict(change),
        can_publish=can_publish,
    )


@bp.post("/projects/<project_id>/changes")
def create_change(project_id):
    project = _project(project_id)
    if not _is_git(_workspace(project)):
        raise ApiError("projeto não é um working copy git")
    _, change = _ensure_draft(project)
    return jsonify(_change_dict(change)), 201


@bp.post("/projects/<project_id>/changes/new")
def new_change(project_id):
    project = _project(project_id)
    workspace = _workspace(project)
    if not _is_git(workspace):
        raise ApiError("projeto não é um working copy git")
    export = _export()
    base = _base(project)
    if export.current_branch(workspace=workspace) != base:
        export.checkout_base(workspace=workspace, base=base)
    return jsonify(branch=base, status="base", change=None, can_publish=False)


@bp.post("/projects/<project_id>/changes/<change_id>/backup")
def backup_change(project_id, change_id):
    project = _project(project_id)
    change = _change_or_404(project, change_id)
    if change.pr_number is not None:
        return jsonify(_change_dict(change))
    repo = _head_repo(project)
    token = _token()
    if not repo or not token:
        raise GitHubSourceError("sem token do provedor; faça login novamente")
    _export().backup(
        workspace=_workspace(project), repo=repo, branch=change.branch, token=token
    )
    return jsonify(_change_dict(change))


@bp.post("/projects/<project_id>/changes/<change_id>/publish")
def publish_change(project_id, change_id):
    project = _project(project_id)
    change = _change_or_404(project, change_id)
    body = request.get_json(silent=True) or {}
    title = (body.get("title") or "").strip()
    if not title:
        raise ApiError("título ausente ou inválido")
    description = body.get("description") or ""
    if not isinstance(description, str):
        raise ApiError("descrição inválida")
    export = _export()
    workspace = _workspace(project)
    base = _base(project)
    upstream = _upstream(project)
    if not upstream:
        raise ApiError("repositório de origem desconhecido")
    token = _token()
    if not token:
        raise GitHubSourceError("sem token do provedor; faça login novamente")
    if not export.has_unpushed(workspace=workspace, branch=change.branch, base=base):
        raise ApiError("não há mudanças para subir")
    target = (
        _unique_branch(project, workspace, _slugify(title))
        if change.branch == EPHEMERAL_BRANCH
        else None
    )
    result = export.publish(
        workspace=workspace,
        upstream=upstream,
        base=base,
        branch=change.branch,
        login=_login(),
        token=token,
        title=title,
        body=description,
        target_branch=target,
    )
    change = _changes().update(
        change.id,
        branch=result.branch,
        title=title,
        pr_number=result.pr_number,
        status="open",
    )
    payload = _change_dict(change)
    payload["url"] = result.url
    payload["created"] = result.created
    _CACHE.clear()
    return jsonify(payload)


@bp.post("/projects/<project_id>/changes/<change_id>/resume")
def resume_change(project_id, change_id):
    project = _project(project_id)
    change = _change_or_404(project, change_id)
    export = _export()
    workspace = _workspace(project)
    base = _base(project)
    export.resume(workspace=workspace, branch=change.branch, base=base)
    if not (workspace / MANIFEST_NAME).is_file():
        export.checkout_base(workspace=workspace, base=base)
        raise NotFoundError("essa alteração não é um projeto do previewer")
    _CACHE.clear()
    return jsonify(_change_dict(change))


@bp.post("/projects/<project_id>/changes/<change_id>/discard")
def discard_change(project_id, change_id):
    project = _project(project_id)
    change = _change_or_404(project, change_id)
    export = _export()
    workspace = _workspace(project)
    base = _base(project)
    repo = _head_repo(project)
    token = _token()
    if change.pr_number is None:
        export.abandon(workspace=workspace, branch=change.branch, base=base)
        _changes().delete(change.id)
    else:
        export.restore(workspace=workspace, branch=change.branch, base=base)
    if repo and token:
        try:
            export.delete_remote_branch(
                repo=repo, branch=backup_branch(change.branch), token=token
            )
        except Exception:
            pass
    _CACHE.clear()
    return jsonify(_change_dict(change))


@bp.delete("/projects/<project_id>/changes/<change_id>")
def abandon_change(project_id, change_id):
    project = _project(project_id)
    change = _change_or_404(project, change_id)
    export = _export()
    workspace = _workspace(project)
    base = _base(project)
    upstream = _upstream(project)
    repo = _head_repo(project)
    token = _token()
    export.abandon(workspace=workspace, branch=change.branch, base=base)
    if token and upstream:
        if change.pr_number:
            try:
                export.close_pull(
                    upstream=upstream, number=change.pr_number, token=token
                )
            except Exception:
                pass
        if repo:
            for branch in (change.branch, backup_branch(change.branch)):
                try:
                    export.delete_remote_branch(
                        repo=repo, branch=branch, token=token
                    )
                except Exception:
                    pass
    _changes().delete(change.id)
    _CACHE.clear()
    return jsonify(ok=True)


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
