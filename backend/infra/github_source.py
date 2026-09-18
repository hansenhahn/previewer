import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

from domain.project import ManifestError, parse_manifest
from infra.git import command as _command
from infra.git import environment as _environment
from infra.ingestion import (
    MANIFEST_NAME,
    InvalidBundleError,
    create_project_for,
    is_unsafe_path,
)

FULL_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*$")
RAW_ROOT = "https://raw.githubusercontent.com"
API_ROOT = "https://api.github.com"


class GitHubSourceError(RuntimeError):
    pass


class GitHubSource:
    def __init__(
        self,
        allow_file: bool = False,
        timeout: int = 180,
        base_url: str = "https://github.com",
    ):
        self.allow_file = allow_file
        self.timeout = timeout
        self.base_url = base_url.rstrip("/")
        self._secrets: tuple[str, ...] = ()

    def _run(self, args, cwd=None, capture: bool = False) -> bytes:
        try:
            result = subprocess.run(
                _command(self.allow_file) + args,
                cwd=cwd,
                env=_environment(),
                capture_output=True,
                timeout=self.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise GitHubSourceError("tempo esgotado ao acessar o repositório") from exc
        if result.returncode != 0:
            message = result.stderr.decode("utf-8", "replace").strip()
            for secret in self._secrets:
                message = message.replace(secret, "***")
            raise GitHubSourceError(message or "falha na operação git")
        return result.stdout if capture else b""

    def fetch(self, *, full_name: str, default_branch: str, working_copy, token=None):
        if not isinstance(full_name, str) or not FULL_NAME.match(full_name):
            raise GitHubSourceError("repositório inválido")
        target = Path(working_copy)
        self._secrets = (token,) if token else ()
        if token:
            url = f"https://x-access-token:{token}@github.com/{full_name}.git"
        else:
            url = f"{self.base_url}/{full_name}.git"
        branch = default_branch or "HEAD"
        self._run(
            [
                "clone",
                "--filter=blob:none",
                "--no-checkout",
                "--depth=1",
                "--branch",
                branch,
                url,
                str(target),
            ]
        )
        raw = self._run(["show", f"HEAD:{MANIFEST_NAME}"], cwd=target, capture=True)
        try:
            manifest = parse_manifest(raw)
        except ManifestError as exc:
            raise InvalidBundleError(str(exc)) from exc
        patterns = self._patterns(manifest)
        self._run(["sparse-checkout", "init", "--no-cone"], cwd=target)
        self._run(["sparse-checkout", "set", "--no-cone", *patterns], cwd=target)
        self._run(["checkout"], cwd=target)
        for asset in (*manifest.fonts, *manifest.backgrounds):
            if not (target / asset.path).is_file():
                raise InvalidBundleError(f"arquivo referenciado ausente: {asset.path}")
        return manifest

    def _patterns(self, manifest) -> list[str]:
        patterns = [MANIFEST_NAME]
        for asset in (*manifest.fonts, *manifest.backgrounds):
            if is_unsafe_path(asset.path):
                raise InvalidBundleError(f"caminho inválido no manifesto: {asset.path!r}")
            patterns.append(asset.path)
        for directory in (manifest.texts.source, manifest.texts.original):
            if not directory:
                continue
            clean = directory.rstrip("/")
            if is_unsafe_path(clean):
                raise InvalidBundleError(f"caminho inválido no manifesto: {directory!r}")
            patterns.append(clean + "/**")
        return patterns


def check_manifest(full_name: str, branch: str, token=None, opener=None):
    if not isinstance(full_name, str) or not FULL_NAME.match(full_name):
        return (False, "repositório inválido")
    open_fn = urllib.request.urlopen if opener is None else opener
    ref = branch or "HEAD"
    if token:
        query = urllib.parse.urlencode({"ref": ref})
        url = f"{API_ROOT}/repos/{full_name}/contents/{MANIFEST_NAME}?{query}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.raw",
            "User-Agent": "previewer",
        }
    else:
        url = f"{RAW_ROOT}/{full_name}/{ref}/{MANIFEST_NAME}"
        headers = {"User-Agent": "previewer"}
    request = urllib.request.Request(url, headers=headers)
    try:
        with open_fn(request) as response:
            data = response.read()
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return (False, "manifest.json ausente")
        return (False, f"falha ao ler o manifest ({error.code})")
    except Exception:
        return (False, "falha ao ler o manifest")
    try:
        parse_manifest(data)
    except ManifestError as error:
        return (False, str(error))
    return (True, None)


def import_repository(
    *,
    storage,
    repository,
    source,
    owner_id,
    full_name,
    default_branch,
    upstream=None,
    base_branch=None,
    token=None,
):
    project_id = uuid.uuid4()
    try:
        storage.create_project(owner_id, str(project_id))
        manifest = source.fetch(
            full_name=full_name,
            default_branch=default_branch,
            working_copy=storage.local_path(owner_id, str(project_id)),
            token=token,
        )
        project = create_project_for(
            repository,
            owner_id,
            manifest,
            project_id=project_id,
            upstream=upstream,
            base_branch=base_branch,
        )
    except Exception:
        storage.delete_project(owner_id, str(project_id))
        raise
    return project, manifest
