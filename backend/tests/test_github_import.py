import json

import pytest
from sqlalchemy.pool import StaticPool

from domain.project import parse_manifest
from infra.db import Database
from infra.identity import Identity, RepositoryRef
from infra.repository import ProjectRepository, RepositoryStore, UserRepository
from infra.storage import FilesystemStorage
from web import create_app
from web.config import Settings
from tests.test_auth import FakeProvider


class FakeSource:
    def __init__(self, name="Projeto Git"):
        self.name = name
        self.calls = []

    def manifest_bytes(self):
        return json.dumps(
            {
                "format": "previewer-project",
                "version": 1,
                "name": self.name,
                "encoding": "windows-1252",
                "texts": {"source": "texts/", "original": None},
                "fonts": [{"name": "f", "path": "fonts/f.NFTR"}],
                "backgrounds": [],
                "screens": [],
            }
        ).encode("utf-8")

    def fetch(self, *, full_name, default_branch, working_copy, token=None):
        self.calls.append((full_name, default_branch))
        working_copy.mkdir(parents=True, exist_ok=True)
        (working_copy / "manifest.json").write_bytes(self.manifest_bytes())
        (working_copy / "fonts").mkdir(exist_ok=True)
        (working_copy / "fonts" / "f.NFTR").write_bytes(b"fonte")
        return parse_manifest(self.manifest_bytes())


@pytest.fixture
def app_client(tmp_path):
    database = Database(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    database.create_all()
    users = UserRepository(database.session_factory)
    user = users.upsert_identity(
        Identity(provider="github", external_id="1", login="alice"),
        access_token="token",
    )
    repositories = RepositoryStore(database.session_factory)
    repositories.refresh(
        user.id,
        "github",
        [
            RepositoryRef(
                provider="github",
                full_name="alice/projeto",
                default_branch="main",
                fork=False,
            ),
            RepositoryRef(
                provider="github",
                full_name="alice/fork-do-projeto",
                default_branch="main",
                fork=True,
            ),
            RepositoryRef(
                provider="github",
                full_name="alice/privado",
                default_branch="main",
                fork=False,
                private=True,
            ),
        ],
    )
    repositories.record_checks(
        user.id,
        "github",
        {
            "alice/projeto": (True, None),
            "alice/fork-do-projeto": (False, "manifest.json ausente"),
            "alice/privado": (True, None),
        },
    )
    settings = Settings(
        storage_root=str(tmp_path),
        database_url="sqlite+pysqlite:///:memory:",
        secret_key="test",
    )
    app = create_app(
        settings,
        database=database,
        storage=FilesystemStorage(tmp_path),
        users=users,
        repositories=repositories,
        identity_provider=FakeProvider(
            repos=[
                RepositoryRef(
                    provider="github",
                    full_name="alice/projeto",
                    default_branch="main",
                    fork=False,
                )
            ]
        ),
        github_source=FakeSource(),
    )
    app.config.update(TESTING=True)
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user_id"] = str(user.id)
        yield client


def test_list_repos_returns_cached(app_client):
    body = app_client.get("/api/github/repos").get_json()
    names = [repo["full_name"] for repo in body["repositories"]]
    assert names == ["alice/fork-do-projeto", "alice/privado", "alice/projeto"]
    assert body["repositories"][0]["fork"] is True
    by_name = {repo["full_name"]: repo for repo in body["repositories"]}
    assert by_name["alice/projeto"]["manifest_ok"] is True
    assert by_name["alice/projeto"]["private"] is False
    assert by_name["alice/privado"]["private"] is True
    assert by_name["alice/fork-do-projeto"]["manifest_ok"] is False
    assert by_name["alice/fork-do-projeto"]["manifest_error"]


def test_refresh_repos(app_client, monkeypatch):
    import infra.github_import as github_import

    monkeypatch.setattr(
        github_import,
        "check_manifest",
        lambda full_name, branch, token=None: (True, None),
    )
    response = app_client.post("/api/github/repos/refresh")
    assert response.status_code == 200
    repos = response.get_json()["repositories"]
    assert [repo["full_name"] for repo in repos] == ["alice/projeto"]
    assert repos[0]["manifest_ok"] is True


def test_import_rejects_repo_without_valid_manifest(app_client):
    response = app_client.post(
        "/api/projects/github", json={"full_name": "alice/fork-do-projeto"}
    )
    assert response.status_code == 422


def test_list_repos_requires_authentication(tmp_path):
    settings = Settings(
        storage_root=str(tmp_path),
        database_url="sqlite+pysqlite:///:memory:",
        secret_key="test",
    )
    app = create_app(settings, database=Database("sqlite+pysqlite:///:memory:"))
    app.config.update(TESTING=True)
    assert app.test_client().get("/api/github/repos").status_code == 401


def test_import_creates_project(app_client):
    response = app_client.post("/api/projects/github", json={"full_name": "alice/projeto"})
    assert response.status_code == 201
    project_id = response.get_json()["id"]
    listing = app_client.get("/api/projects").get_json()["projects"]
    assert [project["id"] for project in listing] == [project_id]
    assert app_client.get(f"/api/projects/{project_id}").status_code == 200


def test_import_rejects_unknown_repository(app_client):
    response = app_client.post("/api/projects/github", json={"full_name": "alice/outro"})
    assert response.status_code == 404


def test_import_requires_full_name(app_client):
    response = app_client.post("/api/projects/github", json={})
    assert response.status_code == 400


def test_import_conflict_on_duplicate(app_client):
    assert app_client.post("/api/projects/github", json={"full_name": "alice/projeto"}).status_code == 201
    response = app_client.post("/api/projects/github", json={"full_name": "alice/projeto"})
    assert response.status_code == 409
