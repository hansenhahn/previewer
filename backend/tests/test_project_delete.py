import io
import uuid

import pytest
from sqlalchemy.pool import StaticPool

from infra.db import Database
from infra.identity import Identity
from infra.repository import ChangeRepository, ProjectRepository, UserRepository
from infra.storage import FilesystemStorage
from tests.fixtures.project import build_bundle
from web import create_app
from web.config import Settings


@pytest.fixture
def ctx(tmp_path):
    database = Database(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    database.create_all()
    users = UserRepository(database.session_factory)
    user = users.upsert_identity(Identity("github", "1", "tester"))
    other = users.upsert_identity(Identity("github", "2", "other"))
    settings = Settings(
        storage_root=str(tmp_path),
        database_url="sqlite+pysqlite:///:memory:",
        secret_key="test",
        github_allowed_users="tester",
    )
    storage = FilesystemStorage(tmp_path)
    app = create_app(settings, database=database, storage=storage, users=users)
    app.config.update(TESTING=True)
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user_id"] = str(user.id)
        yield client, storage, database, user, other


def upload(client):
    data = build_bundle()
    return client.post(
        "/api/projects",
        data={"file": (io.BytesIO(data), "projeto.zip")},
        content_type="multipart/form-data",
    ).get_json()


def test_delete_project_removes_record_changes_and_workspace(ctx):
    client, storage, database, user, _ = ctx
    project = upload(client)
    pid = uuid.UUID(project["id"])
    changes = ChangeRepository(database.session_factory)
    changes.create(pid, user.id, "previewer/sketch")
    workspace = storage.local_path(str(user.id), project["id"])
    assert workspace.exists()

    response = client.delete(f"/api/projects/{project['id']}")

    assert response.status_code == 204
    assert client.get("/api/projects").get_json()["projects"] == []
    assert not workspace.exists()
    assert changes.list_for_user(user.id, pid) == []


def test_delete_missing_project(ctx):
    client, *_ = ctx
    response = client.delete("/api/projects/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_delete_other_owner_not_found(ctx):
    client, storage, database, user, other = ctx
    projects = ProjectRepository(database.session_factory)
    foreign = projects.create(str(other.id), "Outro")
    response = client.delete(f"/api/projects/{foreign.id}")
    assert response.status_code == 404
    assert projects.get(foreign.id) is not None
