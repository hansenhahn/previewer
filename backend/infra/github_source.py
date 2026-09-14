import os
import re
import subprocess
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from domain.project import ManifestError, parse_manifest
from infra.ingestion import (
    MANIFEST_NAME,
    InvalidBundleError,
    create_project_for,
    is_unsafe_path,
)

FULL_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*$")
RAW_ROOT = "https://raw.githubusercontent.com"


class GitHubSourceError(RuntimeError):
    pass


def _command(allow_file: bool) -> list[str]:
    return [
        "git",
        "-c",
        "credential.helper=",
        "-c",
        "protocol.file.allow=" + ("always" if allow_file else "never"),
    ]


def _environment() -> dict:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_ASKPASS"] = "/bin/true"
    return env


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
            raise GitHubSourceError(message or "falha na operação git")
        return result.stdout if capture else b""

    def fetch(self, *, full_name: str, default_branch: str, working_copy):
        if not isinstance(full_name, str) or not FULL_NAME.match(full_name):
            raise GitHubSourceError("repositório inválido")
        target = Path(working_copy)
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


def check_manifest(full_name: str, branch: str, opener=None):
    if not isinstance(full_name, str) or not FULL_NAME.match(full_name):
        return (False, "repositório inválido")
    open_fn = urllib.request.urlopen if opener is None else opener
    url = f"{RAW_ROOT}/{full_name}/{branch or 'HEAD'}/{MANIFEST_NAME}"
    request = urllib.request.Request(url, headers={"User-Agent": "previewer"})
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


def import_repository(*, storage, repository, source, owner_id, full_name, default_branch):
    project_id = uuid.uuid4()
    try:
        storage.create_project(owner_id, str(project_id))
        manifest = source.fetch(
            full_name=full_name,
            default_branch=default_branch,
            working_copy=storage.local_path(owner_id, str(project_id)),
        )
        project = create_project_for(
            repository, owner_id, manifest, project_id=project_id
        )
    except Exception:
        storage.delete_project(owner_id, str(project_id))
        raise
    return project, manifest
