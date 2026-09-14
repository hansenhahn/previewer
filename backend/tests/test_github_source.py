import json
import subprocess
import urllib.error

import pytest

from domain.project import parse_manifest
from infra.github_source import GitHubSource, check_manifest
from infra.ingestion import InvalidBundleError


def _git(*args, cwd):
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        env={
            "PATH": "/usr/bin:/bin:/usr/local/bin",
            "HOME": str(cwd),
            "GIT_CONFIG_NOSYSTEM": "1",
        },
    )


def _manifest(fonts=("fonts/f.NFTR",), text=""):
    document = {
        "format": "previewer-project",
        "version": 1,
        "name": "Projeto Git",
        "encoding": "windows-1252",
        "texts": {"source": "texts/", "original": "original/"},
        "fonts": [{"name": "f", "path": path} for path in fonts],
        "backgrounds": [{"name": "bg", "path": "backgrounds/bg.png"}],
        "screens": [],
    }
    if text:
        document = {**document, **json.loads(text)}
    return json.dumps(document).encode("utf-8")


@pytest.fixture
def remotes(tmp_path):
    work = tmp_path / "work"
    work.mkdir()
    _git("init", "-b", "main", cwd=work)
    _git("config", "user.email", "t@t.test", cwd=work)
    _git("config", "user.name", "t", cwd=work)
    (work / "manifest.json").write_bytes(_manifest())
    for relative, data in (
        ("texts/cap01.txt", b"texto"),
        ("fonts/f.NFTR", b"fonte"),
        ("backgrounds/bg.png", b"png"),
        ("extras/grande.bin", b"nao referenciado"),
    ):
        path = work / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    _git("add", ".", cwd=work)
    _git("commit", "-m", "init", cwd=work)
    root = tmp_path / "remotes"
    target = root / "alice" / "projeto.git"
    target.parent.mkdir(parents=True)
    _git("clone", "--bare", str(work), str(target), cwd=tmp_path)
    return root


def test_fetch_clones_only_referenced_files(tmp_path, remotes):
    working = tmp_path / "copy"
    working.mkdir()
    source = GitHubSource(allow_file=True, base_url=f"file://{remotes}")
    manifest = source.fetch(
        full_name="alice/projeto", default_branch="main", working_copy=working
    )
    assert manifest.name == "Projeto Git"
    assert (working / "manifest.json").is_file()
    assert (working / "texts" / "cap01.txt").is_file()
    assert (working / "fonts" / "f.NFTR").is_file()
    assert (working / "backgrounds" / "bg.png").is_file()
    assert not (working / "extras" / "grande.bin").exists()


def test_fetch_rejects_invalid_full_name(tmp_path):
    source = GitHubSource(allow_file=True)
    with pytest.raises(Exception):
        source.fetch(
            full_name="../etc/passwd",
            default_branch="main",
            working_copy=tmp_path / "copy",
        )


def test_patterns_reject_unsafe_manifest_path():
    manifest = parse_manifest(_manifest(fonts=("../evil.NFTR",)))
    with pytest.raises(InvalidBundleError):
        GitHubSource()._patterns(manifest)


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_check_manifest_valid():
    ok, error = check_manifest(
        "alice/projeto", "main", opener=lambda request: FakeResponse(_manifest())
    )
    assert ok is True
    assert error is None


def test_check_manifest_missing():
    def opener(request):
        raise urllib.error.HTTPError(request.full_url, 404, "not found", {}, None)

    ok, error = check_manifest("alice/projeto", "main", opener=opener)
    assert ok is False
    assert "ausente" in error


def test_check_manifest_invalid():
    ok, error = check_manifest(
        "alice/projeto", "main", opener=lambda request: FakeResponse(b"{ not json")
    )
    assert ok is False
    assert error
