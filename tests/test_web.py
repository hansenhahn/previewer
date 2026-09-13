from app import create_app
from app.config import Settings


class FakeDatabase:
    def __init__(self, healthy: bool):
        self.healthy = healthy

    def is_healthy(self) -> bool:
        return self.healthy


def make_client(healthy: bool = True):
    settings = Settings(
        storage_root="/tmp", database_url="sqlite+pysqlite://", secret_key="test"
    )
    app = create_app(settings, database=FakeDatabase(healthy))
    app.config.update(TESTING=True)
    return app.test_client()


def test_index_returns_html_referencing_static():
    response = make_client().get("/")
    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert b"static" in response.data


def test_static_asset_served_from_same_origin():
    response = make_client().get("/static/app.css")
    assert response.status_code == 200
    assert response.mimetype == "text/css"


def test_healthz_healthy():
    response = make_client(True).get("/healthz")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_healthz_degraded():
    response = make_client(False).get("/healthz")
    assert response.status_code == 503
    assert response.get_json()["status"] == "degraded"


def test_healthz_requires_no_authentication():
    response = make_client().get("/healthz")
    assert response.status_code in (200, 503)
