import subprocess

import pytest

from infra.git import GitError
from infra.project_export import (
    GitHubProjectExport,
    ProjectExport,
    ProjectExportError,
    _changes_requested,
    _push_error,
    parse_upstream,
)
from tests.fakes import FakeProjectExport


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


def _count(path, revision_range):
    result = subprocess.run(
        ["git", "rev-list", "--count", revision_range],
        cwd=path,
        check=True,
        capture_output=True,
        env={
            "PATH": "/usr/bin:/bin:/usr/local/bin",
            "HOME": str(path),
            "GIT_CONFIG_NOSYSTEM": "1",
        },
    )
    return int(result.stdout.decode().strip())


@pytest.fixture
def workspace(tmp_path):
    work = tmp_path / "work"
    work.mkdir()
    _git("init", "-b", "main", cwd=work)
    _git("config", "user.email", "t@t.test", cwd=work)
    _git("config", "user.name", "t", cwd=work)
    (work / "texts").mkdir()
    (work / "texts" / "cap01.txt").write_text("original")
    _git("add", ".", cwd=work)
    _git("commit", "-m", "init", cwd=work)
    origin = tmp_path / "origin.git"
    _git("clone", "--bare", str(work), str(origin), cwd=tmp_path)
    copy = tmp_path / "copy"
    _git("clone", str(origin), str(copy), cwd=tmp_path)
    return copy


class FakeClient:
    def __init__(
        self, *, pull=None, state=None, reviews=None, pulls=None, manifests=None
    ):
        self.calls = []
        self.pull = pull
        self.state = state or {"state": "open", "merged": False}
        self.reviews = reviews or []
        self.pulls = pulls or []
        self.manifests = set(manifests or [])

    def ensure_fork(self, *, upstream, login, token):
        self.calls.append(("ensure_fork", upstream, login))
        return f"{login}/{upstream.split('/')[-1]}"

    def merge_upstream(self, *, fork, branch, token):
        self.calls.append(("merge_upstream", fork, branch))

    def find_pull(self, *, upstream, head, base, token):
        self.calls.append(("find_pull", head))
        return self.pull

    def create_pull(self, *, upstream, head, base, title, body, token):
        self.calls.append(("create_pull", head))
        return {"number": 12, "html_url": "https://github.com/x/y/pull/12"}

    def list_pulls(self, *, upstream, state, token):
        self.calls.append(("list_pulls", state))
        return self.pulls

    def branch_has_manifest(self, *, repo, branch, token):
        return branch in self.manifests

    def pull_state(self, *, upstream, number, token):
        return self.state

    def pull_reviews(self, *, upstream, number, token):
        return self.reviews

    def close_pull(self, *, upstream, number, token):
        self.calls.append(("close_pull", number))

    def delete_branch(self, *, repo, branch, token):
        self.calls.append(("delete_branch", branch))


def export_for(workspace, **kwargs):
    return GitHubProjectExport(client=kwargs.pop("client", FakeClient()), allow_file=True, **kwargs)


def test_contract_is_satisfied_by_concrete_and_fake(workspace):
    assert isinstance(GitHubProjectExport(client=FakeClient()), ProjectExport)
    assert isinstance(FakeProjectExport(), ProjectExport)


def test_parse_upstream():
    assert parse_upstream("https://github.com/alice/projeto.git") == "alice/projeto"
    assert parse_upstream("git@github.com:alice/projeto.git") == "alice/projeto"
    assert parse_upstream("https://github.com/alice/projeto") == "alice/projeto"
    assert parse_upstream("file:///tmp/remotes/alice/projeto.git") is None


def test_ensure_branch_creates_from_base(workspace):
    export = export_for(workspace)
    export.ensure_branch(workspace=workspace, branch="previewer/x", base="main")
    assert export.current_branch(workspace=workspace) == "previewer/x"
    assert export.branch_exists(workspace=workspace, branch="previewer/x")
    assert export.default_branch(workspace=workspace) == "main"


def test_ensure_branch_uses_latest_base(workspace, tmp_path):
    origin = workspace.parent / "origin.git"
    other = tmp_path / "other"
    _git("clone", str(origin), str(other), cwd=tmp_path)
    _git("config", "user.email", "t@t.test", cwd=other)
    _git("config", "user.name", "t", cwd=other)
    (other / "texts" / "cap03.txt").write_text("novo")
    _git("add", ".", cwd=other)
    _git("commit", "-m", "upstream", cwd=other)
    _git("push", "origin", "main", cwd=other)

    export = export_for(workspace)
    export.ensure_branch(workspace=workspace, branch="previewer/y", base="main")
    assert (workspace / "texts" / "cap03.txt").is_file()


def test_commit_creates_one_commit_per_autosave(workspace):
    export = export_for(workspace)
    branch = "previewer/x"
    export.ensure_branch(workspace=workspace, branch=branch, base="main")
    (workspace / "texts" / "cap01.txt").write_text("v1")
    export.commit(workspace=workspace, branch=branch, base="main", message="rascunho")
    assert _count(workspace, "origin/main..HEAD") == 1
    (workspace / "texts" / "cap01.txt").write_text("v2")
    export.commit(workspace=workspace, branch=branch, base="main", message="rascunho")
    assert _count(workspace, "origin/main..HEAD") == 2


def test_has_unpushed_and_restore(workspace):
    export = export_for(workspace)
    branch = "previewer/x"
    export.ensure_branch(workspace=workspace, branch=branch, base="main")
    assert export.has_unpushed(workspace=workspace, branch=branch, base="main") is False
    (workspace / "texts" / "cap01.txt").write_text("editado")
    assert export.has_uncommitted(workspace=workspace) is True
    export.commit(
        workspace=workspace, branch=branch, base="main", message="rascunho"
    )
    assert export.has_unpushed(workspace=workspace, branch=branch, base="main") is True
    export.restore(workspace=workspace, branch=branch, base="main")
    assert export.has_uncommitted(workspace=workspace) is False
    assert export.has_unpushed(workspace=workspace, branch=branch, base="main") is False
    assert (workspace / "texts" / "cap01.txt").read_text() == "original"


def test_resume_allows_unpublished_commits(workspace):
    export = export_for(workspace)
    first = "previewer/a"
    second = "previewer/b"
    export.ensure_branch(workspace=workspace, branch=first, base="main")
    _git("branch", second, "origin/main", cwd=workspace)
    (workspace / "texts" / "cap01.txt").write_text("wip")
    export.commit(workspace=workspace, branch=first, base="main", message="wip")
    export.resume(workspace=workspace, branch=second, base="main")
    assert export.current_branch(workspace=workspace) == second
    export.resume(workspace=workspace, branch=first, base="main")
    assert export.current_branch(workspace=workspace) == first


def test_resume_blocks_unsaved_changes(workspace):
    export = export_for(workspace)
    first = "previewer/a"
    second = "previewer/b"
    export.ensure_branch(workspace=workspace, branch=first, base="main")
    _git("branch", second, "origin/main", cwd=workspace)
    (workspace / "texts" / "cap01.txt").write_text("nao salvo")
    with pytest.raises(ProjectExportError):
        export.resume(workspace=workspace, branch=second, base="main")
    export.restore(workspace=workspace, branch=first, base="main")
    export.resume(workspace=workspace, branch=second, base="main")
    assert export.current_branch(workspace=workspace) == second


def test_resume_fetches_missing_branch_from_origin(workspace, tmp_path):
    origin = workspace.parent / "origin.git"
    other = tmp_path / "other"
    _git("clone", str(origin), str(other), cwd=tmp_path)
    _git("config", "user.email", "t@t.test", cwd=other)
    _git("config", "user.name", "t", cwd=other)
    _git("checkout", "-b", "previewer/other", cwd=other)
    (other / "texts" / "cap09.txt").write_text("x")
    _git("add", ".", cwd=other)
    _git("commit", "-m", "other", cwd=other)
    _git("push", "origin", "previewer/other", cwd=other)

    export = export_for(workspace)
    export.resume(workspace=workspace, branch="previewer/other", base="main")
    assert export.current_branch(workspace=workspace) == "previewer/other"


def test_abandon_removes_branch_and_returns_to_base(workspace):
    export = export_for(workspace)
    branch = "previewer/x"
    export.ensure_branch(workspace=workspace, branch=branch, base="main")
    export.abandon(workspace=workspace, branch=branch, base="main")
    assert export.current_branch(workspace=workspace) == "main"
    assert export.branch_exists(workspace=workspace, branch=branch) is False


def test_origin_remote_parses_origin(workspace):
    export = export_for(workspace)
    _git(
        "remote",
        "set-url",
        "origin",
        "https://github.com/alice/projeto.git",
        cwd=workspace,
    )
    assert export.origin_remote(workspace=workspace) == "alice/projeto"


def test_checkout_base_returns_to_base(workspace):
    export = export_for(workspace)
    branch = "previewer/x"
    export.ensure_branch(workspace=workspace, branch=branch, base="main")
    export.checkout_base(workspace=workspace, base="main")
    assert export.current_branch(workspace=workspace) == "main"


def test_backup_pushes_commits_to_backup_branch(workspace, fork):
    client = FakeClient()
    export = LocalForkExport(fork, client=client, allow_file=True)
    branch = "previewer/x"
    export.ensure_branch(workspace=workspace, branch=branch, base="main")
    (workspace / "texts" / "cap01.txt").write_text("wip")
    export.commit(workspace=workspace, branch=branch, base="main", message="wip")
    export.backup(workspace=workspace, repo="alice/projeto", branch=branch, token="tok")
    pushed = subprocess.run(
        ["git", "rev-parse", "--verify", "refs/heads/previewer-backup/x"],
        cwd=fork,
        capture_output=True,
    )
    assert pushed.returncode == 0


class LocalForkExport(GitHubProjectExport):
    def __init__(self, fork_path, upstream_path=None, **kwargs):
        super().__init__(**kwargs)
        self.fork_path = fork_path
        self.upstream_path = upstream_path or fork_path

    def _fork_url(self, fork, token):
        return str(self.fork_path)

    def _upstream_url(self, upstream, token):
        return str(self.upstream_path)


@pytest.fixture
def fork(tmp_path, workspace):
    fork_path = tmp_path / "fork.git"
    _git("clone", "--bare", str(workspace), str(fork_path), cwd=tmp_path)
    return fork_path


def test_publish_pushes_branch_and_opens_pull_request(workspace, fork):
    client = FakeClient()
    export = LocalForkExport(
        fork, upstream_path=workspace.parent / "origin.git", client=client, allow_file=True
    )
    branch = "previewer/x"
    export.ensure_branch(workspace=workspace, branch=branch, base="main")
    for text in ("v1", "v2", "contribuicao"):
        (workspace / "texts" / "cap01.txt").write_text(text)
        export.commit(
            workspace=workspace, branch=branch, base="main", message="autosave"
        )
    assert _count(workspace, "origin/main..HEAD") == 3
    result = export.publish(
        workspace=workspace,
        upstream="alice/projeto",
        base="main",
        branch=branch,
        login="alice",
        token="tok",
        title="capítulo 3",
        body="descrição",
    )
    assert _count(workspace, "origin/main..HEAD") == 1
    assert result.pr_number == 12
    assert result.created is True
    assert ("create_pull", "alice:previewer/x") in client.calls
    assert ("ensure_fork", "alice/projeto", "alice") in client.calls
    assert ("merge_upstream", "alice/projeto", "main") in client.calls
    pushed = subprocess.run(
        ["git", "rev-parse", "--verify", f"refs/heads/{branch}"],
        cwd=fork,
        capture_output=True,
    )
    assert pushed.returncode == 0
    assert export.has_unpushed(workspace=workspace, branch=branch, base="main") is False
    assert ("delete_branch", "previewer-backup/x") in client.calls


def test_publish_reuses_existing_pull_request(workspace, fork):
    client = FakeClient(pull={"number": 9, "html_url": "https://github.com/x/y/pull/9"})
    export = LocalForkExport(
        fork, upstream_path=workspace.parent / "origin.git", client=client, allow_file=True
    )
    branch = "previewer/x"
    export.ensure_branch(workspace=workspace, branch=branch, base="main")
    (workspace / "texts" / "cap01.txt").write_text("um")
    export.publish(
        workspace=workspace,
        upstream="alice/projeto",
        base="main",
        branch=branch,
        login="alice",
        token="tok",
        title="um",
        body="",
    )
    (workspace / "texts" / "cap01.txt").write_text("dois")
    result = export.publish(
        workspace=workspace,
        upstream="alice/projeto",
        base="main",
        branch=branch,
        login="alice",
        token="tok",
        title="dois",
        body="",
    )
    assert result.created is False
    assert result.pr_number == 9
    assert ("create_pull", "alice:previewer/x") not in client.calls
    assert _count(workspace, "origin/main..HEAD") == 2


def test_publish_renames_ephemeral_branch(workspace, fork):
    client = FakeClient()
    export = LocalForkExport(
        fork, upstream_path=workspace.parent / "origin.git", client=client, allow_file=True
    )
    export.ensure_branch(workspace=workspace, branch="previewer/sketch", base="main")
    (workspace / "texts" / "cap01.txt").write_text("x")
    export.commit(
        workspace=workspace, branch="previewer/sketch", base="main", message="x"
    )
    result = export.publish(
        workspace=workspace,
        upstream="alice/projeto",
        base="main",
        branch="previewer/sketch",
        login="alice",
        token="tok",
        title="Cap 1",
        body="",
        target_branch="previewer/cap-1",
    )
    assert result.branch == "previewer/cap-1"
    assert export.current_branch(workspace=workspace) == "previewer/cap-1"
    assert export.branch_exists(workspace=workspace, branch="previewer/cap-1")
    assert ("create_pull", "alice:previewer/cap-1") in client.calls
    pushed = subprocess.run(
        ["git", "rev-parse", "--verify", "refs/heads/previewer/cap-1"],
        cwd=fork,
        capture_output=True,
    )
    assert pushed.returncode == 0


def test_sync_merges_advanced_upstream(workspace, tmp_path):
    origin = workspace.parent / "origin.git"
    export = export_for(workspace)
    _git("remote", "add", "upstream", str(origin), cwd=workspace)
    branch = "previewer/x"
    export.ensure_branch(workspace=workspace, branch=branch, base="main")
    (workspace / "texts" / "cap01.txt").write_text("contribuicao")
    export.commit(
        workspace=workspace, branch=branch, base="main", message="rascunho"
    )

    other = tmp_path / "other"
    _git("clone", str(origin), str(other), cwd=tmp_path)
    _git("config", "user.email", "t@t.test", cwd=other)
    _git("config", "user.name", "t", cwd=other)
    (other / "texts" / "cap02.txt").write_text("novo")
    _git("add", ".", cwd=other)
    _git("commit", "-m", "upstream", cwd=other)
    _git("push", "origin", "main", cwd=other)

    updated = export.sync(
        workspace=workspace, upstream="alice/projeto", base="main", branch=branch, token="t"
    )
    assert updated is True
    assert (workspace / "texts" / "cap02.txt").is_file()
    again = export.sync(
        workspace=workspace, upstream="alice/projeto", base="main", branch=branch, token="t"
    )
    assert again is False


def test_open_pulls_filters_by_head_repo_and_marks_resumable():
    client = FakeClient(
        pulls=[
            {
                "number": 14,
                "title": "t",
                "head": {"ref": "previewer/a", "repo": {"full_name": "alice/projeto"}},
            },
            {
                "number": 15,
                "title": "outro",
                "head": {"ref": "previewer/b", "repo": {"full_name": "someone/projeto"}},
            },
            {
                "number": 7,
                "title": "revisão",
                "head": {"ref": "revisao/cap-2", "repo": {"full_name": "alice/projeto"}},
            },
        ],
        manifests=["previewer/a"],
    )
    export = GitHubProjectExport(client=client)
    refs = export.open_pulls(
        upstream="alice/projeto", head_repo="alice/projeto", token="t"
    )
    assert [(ref.number, ref.branch, ref.resumable) for ref in refs] == [
        (14, "previewer/a", True),
        (7, "revisao/cap-2", False),
    ]


def test_pr_status_maps_reviews_and_merge():
    client = FakeClient(
        reviews=[{"state": "CHANGES_REQUESTED", "user": {"login": "rev"}}]
    )
    export = GitHubProjectExport(client=client)
    assert (
        export.pr_status(upstream="alice/projeto", number=1, token="t").state
        == "changes_requested"
    )
    client.state = {"state": "closed", "merged": True}
    assert (
        export.pr_status(upstream="alice/projeto", number=1, token="t").state
        == "merged"
    )
    client.state = {"state": "closed", "merged": False}
    assert (
        export.pr_status(upstream="alice/projeto", number=1, token="t").state
        == "closed"
    )


def test_push_error_maps_permission_denied():
    denied = _push_error(
        GitError("remote: Permission to x denied to y. fatal: ... 403")
    )
    assert "public_repo" in str(denied)
    assert str(_push_error(GitError("outro erro"))) == "outro erro"


def test_changes_requested_latest_review_wins():
    reviews = [
        {"state": "CHANGES_REQUESTED", "user": {"login": "rev"}},
        {"state": "APPROVED", "user": {"login": "rev"}},
    ]
    assert _changes_requested(reviews) is False
