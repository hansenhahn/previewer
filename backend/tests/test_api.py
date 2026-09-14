import io

import pytest
from sqlalchemy.pool import StaticPool

from web import create_app
from web.config import Settings
from infra.db import Database
from infra.storage import FilesystemStorage
from tests.fixtures.project import build_bundle


@pytest.fixture
def client(tmp_path):
    database = Database(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    database.create_all()
    settings = Settings(
        storage_root=str(tmp_path),
        database_url="sqlite+pysqlite:///:memory:",
        secret_key="test",
    )
    app = create_app(settings, database=database, storage=FilesystemStorage(tmp_path))
    app.config.update(TESTING=True)
    return app.test_client()


def upload(client, **kwargs):
    data = build_bundle(**kwargs)
    return client.post(
        "/api/projects",
        data={"file": (io.BytesIO(data), "projeto.zip")},
        content_type="multipart/form-data",
    )


def test_list_projects_empty(client):
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert response.get_json()["projects"] == []


def test_upload_and_list(client):
    response = upload(client)
    assert response.status_code == 201
    project_id = response.get_json()["id"]

    listing = client.get("/api/projects").get_json()["projects"]
    assert [project["id"] for project in listing] == [project_id]


def test_get_project(client):
    project_id = upload(client).get_json()["id"]
    response = client.get(f"/api/projects/{project_id}")
    assert response.status_code == 200
    body = response.get_json()
    assert body["manifest"]["name"] == "Meu Projeto"
    assert body["manifest"]["fonts"][0]["name"] == "fontevent"


def test_get_missing_project(client):
    response = client.get("/api/projects/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_list_files(client):
    project_id = upload(client).get_json()["id"]
    response = client.get(f"/api/projects/{project_id}/files")
    assert response.status_code == 200
    assert "texts/cap01.txt" in response.get_json()["files"]


def test_read_file_uses_project_encoding(client):
    project_id = upload(client).get_json()["id"]
    response = client.get(f"/api/projects/{project_id}/files/texts/cap01.txt")
    assert response.status_code == 200
    assert response.get_json()["content"] == "texto"


def test_read_missing_file(client):
    project_id = upload(client).get_json()["id"]
    response = client.get(f"/api/projects/{project_id}/files/texts/nope.txt")
    assert response.status_code == 404


def test_write_file_roundtrip(client):
    project_id = upload(client).get_json()["id"]
    path = f"/api/projects/{project_id}/files/texts/cap01.txt"
    saved = client.put(path, json={"content": "nova linha"})
    assert saved.status_code == 200
    assert client.get(path).get_json()["content"] == "nova linha"


def test_atlas_json_and_png(client):
    project_id = upload(client).get_json()["id"]
    metrics = client.get(f"/api/projects/{project_id}/fonts/fontevent/atlas")
    assert metrics.status_code == 200
    body = metrics.get_json()
    assert body["line_height"] == 12
    assert len(body["glyphs"]) > 0
    assert body["image"]["url"].endswith("/atlas.png")

    image = client.get(f"/api/projects/{project_id}/fonts/fontevent/atlas.png")
    assert image.status_code == 200
    assert image.mimetype == "image/png"
    assert image.data[:8] == b"\x89PNG\r\n\x1a\n"


def test_atlas_unknown_font(client):
    project_id = upload(client).get_json()["id"]
    response = client.get(f"/api/projects/{project_id}/fonts/nope/atlas")
    assert response.status_code == 404


def test_atlas_unsupported_font(client):
    project_id = upload(client, font_bytes=b"nao e uma fonte").get_json()["id"]
    response = client.get(f"/api/projects/{project_id}/fonts/fontevent/atlas")
    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "unsupported_font"


def test_layout_endpoint_removed(client):
    project_id = upload(client).get_json()["id"]
    response = client.post(
        f"/api/projects/{project_id}/screens/default/layout", json={"text": "AB"}
    )
    assert response.status_code == 404


def test_atlas_metrics_include_default_advance(client):
    project_id = upload(client).get_json()["id"]
    body = client.get(f"/api/projects/{project_id}/fonts/fontevent/atlas").get_json()
    assert body["default_advance"] == 18


def test_background_served(client):
    project_id = upload(client).get_json()["id"]
    response = client.get(f"/api/projects/{project_id}/backgrounds/bg1")
    assert response.status_code == 200
    assert response.mimetype == "image/png"


def test_background_unknown(client):
    project_id = upload(client).get_json()["id"]
    response = client.get(f"/api/projects/{project_id}/backgrounds/nope")
    assert response.status_code == 404


def test_background_traversal_name_rejected(client):
    project_id = upload(client).get_json()["id"]
    response = client.get(f"/api/projects/{project_id}/backgrounds/..")
    assert response.status_code == 404


def test_read_original_variant(client):
    project_id = upload(client).get_json()["id"]
    response = client.get(
        f"/api/projects/{project_id}/files/texts/cap01.txt?variant=original"
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["content"] == "original"
    assert body["variant"] == "original"


def test_read_original_missing(client):
    project_id = upload(client).get_json()["id"]
    response = client.get(
        f"/api/projects/{project_id}/files/texts/nope.txt?variant=original"
    )
    assert response.status_code == 404


def test_read_source_variant_unchanged(client):
    project_id = upload(client).get_json()["id"]
    response = client.get(
        f"/api/projects/{project_id}/files/texts/cap01.txt?variant=source"
    )
    assert response.status_code == 200
    assert response.get_json()["content"] == "texto"
