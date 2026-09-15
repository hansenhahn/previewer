import io
import json
import urllib.error

import pytest

from infra.github_export import GitHubExportClient, GitHubExportError


class FakeResponse:
    def __init__(self, payload):
        self._payload = (
            b"" if payload is None else json.dumps(payload).encode("utf-8")
        )

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def make_opener(routes):
    def _open(request):
        method = request.get_method()
        for (expected, fragment), payload in routes.items():
            if expected == method and fragment in request.full_url:
                if callable(payload):
                    payload(request)
                if isinstance(payload, Exception):
                    raise payload
                return FakeResponse(payload)
        raise AssertionError(f"URL inesperada: {method} {request.full_url}")

    return _open


def not_found(request):
    raise urllib.error.HTTPError(request.full_url, 404, "not found", {}, None)


def test_ensure_fork_creates_when_missing():
    created = {}
    routes = {
        ("GET", "/repos/alice/projeto"): not_found,
        ("POST", "/repos/upstream/projeto/forks"): {},
    }

    def opener(request):
        if request.get_method() == "POST":
            created["body"] = request.data
        return make_opener(routes)(request)

    client = GitHubExportClient(opener=opener)
    fork = client.ensure_fork(
        upstream="upstream/projeto", login="alice", token="t"
    )
    assert fork == "alice/projeto"
    assert created["body"] == b"{}"


def test_ensure_fork_reuses_existing_fork():
    client = GitHubExportClient(
        opener=make_opener(
            {
                ("GET", "/repos/alice/projeto"): {
                    "fork": True,
                    "parent": {"full_name": "upstream/projeto"},
                }
            }
        )
    )
    assert (
        client.ensure_fork(upstream="upstream/projeto", login="alice", token="t")
        == "alice/projeto"
    )


def test_ensure_fork_accepts_own_repository():
    client = GitHubExportClient(
        opener=make_opener(
            {
                ("GET", "/repos/alice/projeto"): {
                    "full_name": "alice/projeto",
                    "fork": False,
                    "parent": None,
                }
            }
        )
    )
    assert (
        client.ensure_fork(upstream="alice/projeto", login="alice", token="t")
        == "alice/projeto"
    )


def test_ensure_fork_rejects_unrelated_repository():
    client = GitHubExportClient(
        opener=make_opener(
            {
                ("GET", "/repos/alice/projeto"): {
                    "fork": False,
                    "parent": None,
                }
            }
        )
    )
    with pytest.raises(GitHubExportError):
        client.ensure_fork(
            upstream="upstream/projeto", login="alice", token="t"
        )


def test_branch_has_manifest():
    present = GitHubExportClient(
        opener=make_opener(
            {
                ("GET", "/repos/alice/projeto/contents/manifest.json"): {
                    "name": "manifest.json"
                }
            }
        )
    )
    assert (
        present.branch_has_manifest(
            repo="alice/projeto", branch="previewer/x", token="t"
        )
        is True
    )
    missing = GitHubExportClient(
        opener=make_opener(
            {
                ("GET", "/repos/alice/projeto/contents/manifest.json"): not_found,
            }
        )
    )
    assert (
        missing.branch_has_manifest(
            repo="alice/projeto", branch="revisao/x", token="t"
        )
        is False
    )


def test_delete_branch_tolerates_missing():
    client = GitHubExportClient(
        opener=make_opener({("DELETE", "/repos/alice/projeto/git/refs/"): not_found})
    )
    assert client.delete_branch(repo="alice/projeto", branch="previewer/x", token="t") is None


def test_error_message_uses_api_message():
    def opener(request):
        raise urllib.error.HTTPError(
            request.full_url,
            422,
            "unprocessable",
            {},
            io.BytesIO(json.dumps({"message": "Validation Failed"}).encode("utf-8")),
        )

    client = GitHubExportClient(opener=opener)
    with pytest.raises(GitHubExportError, match="Validation Failed"):
        client.create_pull(
            upstream="a/b", head="alice:x", base="main", title="t", body="", token="t"
        )
