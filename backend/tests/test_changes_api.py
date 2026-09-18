import json
import subprocess

import pytest
from sqlalchemy.pool import StaticPool

from infra.db import Database
from infra.identity import Identity
from infra.repository import ChangeRepository, ProjectRepository, UserRepository
from infra.project_export import PullRef
from infra.storage import FilesystemStorage
from tests.fakes import FakeProjectExport
from tests.fixtures.project import manifest_document
from web import create_app
from web.config import Settings


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


@pytest.fixture
def context(tmp_path):
    database = Database(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    database.create_all()
    users = UserRepository(database.session_factory)
    user = users.upsert_identity(
        Identity("github", "1", "alice"), access_token="token"
    )
    projects = ProjectRepository(database.session_factory)
    project = projects.create(str(user.id), "Projeto")
    storage = FilesystemStorage(tmp_path / "storage")
    workspace = storage.local_path(str(user.id), str(project.id))
    workspace.mkdir(parents=True)
    _git("init", "-b", "main", cwd=workspace)
    _git("config", "user.email", "t@t.test", cwd=workspace)
    _git("config", "user.name", "t", cwd=workspace)
    (workspace / "texts").mkdir()
    (workspace / "texts" / "cap01.txt").write_text("texto")
    (workspace / "manifest.json").write_text(json.dumps(manifest_document()))
    _git("add", ".", cwd=workspace)
    _git("commit", "-m", "init", cwd=workspace)
    changes = ChangeRepository(database.session_factory)
    export = FakeProjectExport()
    settings = Settings(
        storage_root=str(tmp_path / "storage"),
        database_url="sqlite+pysqlite:///:memory:",
        secret_key="test",
        github_allowed_users="alice",
    )
    app = create_app(
        settings,
        database=database,
        storage=storage,
        users=users,
        projects=projects,
        changes=changes,
        project_export=export,
    )
    app.config.update(TESTING=True)
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user_id"] = str(user.id)
        yield client, project, export


def test_state_starts_at_base(context):
    client, project, _ = context
    body = client.get(f"/api/projects/{project.id}/changes/state").get_json()
    assert body["status"] == "base"
    assert body["change"] is None


def test_first_edit_creates_draft_branch(context):
    client, project, export = context
    response = client.put(
        f"/api/projects/{project.id}/files/texts/cap01.txt",
        json={"content": "editado"},
    )
    assert response.status_code == 200
    change = response.get_json()["change"]
    assert change["branch"] == "previewer/sketch"
    assert change["status"] == "draft"
    assert export.branch == change["branch"]
    assert ("ensure_branch", change["branch"]) in export.calls

    listing = client.get(f"/api/projects/{project.id}/changes").get_json()["changes"]
    assert [item["id"] for item in listing] == [change["id"]]

    state = client.get(f"/api/projects/{project.id}/changes/state").get_json()
    assert state["status"] == "draft"
    assert state["change"]["id"] == change["id"]


def test_second_edit_reuses_same_draft(context):
    client, project, _ = context
    first = client.put(
        f"/api/projects/{project.id}/files/texts/cap01.txt", json={"content": "a"}
    ).get_json()["change"]
    second = client.put(
        f"/api/projects/{project.id}/files/texts/cap01.txt", json={"content": "b"}
    ).get_json()["change"]
    assert first["id"] == second["id"]


def test_publish_requires_pending_changes(context):
    client, project, export = context
    client.put(
        f"/api/projects/{project.id}/files/texts/cap01.txt", json={"content": "a"}
    )
    response = client.post(
        f"/api/projects/{project.id}/changes/{_only_change(client, project)}/publish",
        json={"title": "Capítulo 1"},
    )
    assert response.status_code == 400


def test_publish_opens_pull_request(context):
    client, project, export = context
    change = client.put(
        f"/api/projects/{project.id}/files/texts/cap01.txt", json={"content": "a"}
    ).get_json()["change"]
    export.pending = True
    response = client.post(
        f"/api/projects/{project.id}/changes/{change['id']}/publish",
        json={"title": "Capítulo 1", "description": "desc"},
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["pr_number"] == 12
    assert body["status"] == "open"
    assert body["branch"] == "previewer/capitulo-1"
    assert ("publish", "Capítulo 1") in export.calls


def test_resume_and_discard_draft(context):
    client, project, export = context
    change = client.put(
        f"/api/projects/{project.id}/files/texts/cap01.txt", json={"content": "a"}
    ).get_json()["change"]
    resumed = client.post(
        f"/api/projects/{project.id}/changes/{change['id']}/resume"
    )
    assert resumed.status_code == 200
    assert ("resume", change["branch"]) in export.calls

    discarded = client.post(
        f"/api/projects/{project.id}/changes/{change['id']}/discard"
    )
    assert discarded.status_code == 200
    assert ("abandon", change["branch"]) in export.calls
    assert client.get(f"/api/projects/{project.id}/changes").get_json()["changes"] == []


def test_discard_published_resets_work(context):
    client, project, export = context
    change = client.put(
        f"/api/projects/{project.id}/files/texts/cap01.txt", json={"content": "a"}
    ).get_json()["change"]
    export.pending = True
    published = client.post(
        f"/api/projects/{project.id}/changes/{change['id']}/publish",
        json={"title": "t"},
    ).get_json()
    discarded = client.post(
        f"/api/projects/{project.id}/changes/{change['id']}/discard"
    )
    assert discarded.status_code == 200
    assert ("restore", published["branch"]) in export.calls


def test_abandon_removes_change(context):
    client, project, export = context
    change = client.put(
        f"/api/projects/{project.id}/files/texts/cap01.txt", json={"content": "a"}
    ).get_json()["change"]
    abandoned = client.delete(f"/api/projects/{project.id}/changes/{change['id']}")
    assert abandoned.status_code == 200
    assert ("abandon", change["branch"]) in export.calls
    assert client.get(f"/api/projects/{project.id}/changes").get_json()["changes"] == []


def test_abandon_closes_pull_request(context):
    client, project, export = context
    change = client.put(
        f"/api/projects/{project.id}/files/texts/cap01.txt", json={"content": "a"}
    ).get_json()["change"]
    export.pending = True
    published = client.post(
        f"/api/projects/{project.id}/changes/{change['id']}/publish",
        json={"title": "t"},
    ).get_json()
    client.delete(f"/api/projects/{project.id}/changes/{change['id']}")
    assert ("close_pull", 12) in export.calls
    assert ("delete_remote_branch", published["branch"]) in export.calls


def test_list_changes_syncs_open_pulls(context):
    client, project, export = context
    export.pulls = [
        PullRef(number=14, branch="previewer/teste", title="Teste")
    ]
    listing = client.get(
        f"/api/projects/{project.id}/changes?sync=1"
    ).get_json()["changes"]
    synced = [item for item in listing if item["branch"] == "previewer/teste"]
    assert len(synced) == 1
    assert synced[0]["pr_number"] == 14
    assert synced[0]["status"] == "open"
    again = client.get(
        f"/api/projects/{project.id}/changes?sync=1"
    ).get_json()["changes"]
    assert len([item for item in again if item["branch"] == "previewer/teste"]) == 1


def test_backup_route(context):
    client, project, export = context
    change = client.put(
        f"/api/projects/{project.id}/files/texts/cap01.txt", json={"content": "a"}
    ).get_json()["change"]
    response = client.post(
        f"/api/projects/{project.id}/changes/{change['id']}/backup"
    )
    assert response.status_code == 200
    assert ("backup", "alice/projeto", change["branch"]) in export.calls


def test_backup_skips_published_change(context):
    client, project, export = context
    change = client.put(
        f"/api/projects/{project.id}/files/texts/cap01.txt", json={"content": "a"}
    ).get_json()["change"]
    export.pending = True
    client.post(
        f"/api/projects/{project.id}/changes/{change['id']}/publish",
        json={"title": "t"},
    )
    before = sum(1 for call in export.calls if call[0] == "backup")
    response = client.post(
        f"/api/projects/{project.id}/changes/{change['id']}/backup"
    )
    assert response.status_code == 200
    assert sum(1 for call in export.calls if call[0] == "backup") == before


def test_new_change_returns_to_base(context):
    client, project, export = context
    client.put(
        f"/api/projects/{project.id}/files/texts/cap01.txt", json={"content": "a"}
    )
    response = client.post(f"/api/projects/{project.id}/changes/new")
    assert response.status_code == 200
    assert response.get_json()["status"] == "base"
    assert ("checkout_base", "main") in export.calls


def test_change_missing_returns_not_found(context):
    client, project, _ = context
    response = client.post(
        f"/api/projects/{project.id}/changes/00000000-0000-0000-0000-000000000000/resume"
    )
    assert response.status_code == 404


def _only_change(client, project):
    return client.get(f"/api/projects/{project.id}/changes").get_json()["changes"][0][
        "id"
    ]
