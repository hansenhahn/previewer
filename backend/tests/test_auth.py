import pytest
from sqlalchemy.pool import StaticPool

from infra.db import Database
from infra.identity import Authorization, Identity, IdentityError
from infra.repository import UserRepository
from web import create_app
from web.config import Settings


class FakeProvider:
    name = "fake"
    label = "Exemplo"

    def __init__(self, identity=None, error=None, repos=None):
        self.identity = identity
        self.error = error
        self.repos = repos or []
        self.states = []

    def login_url(self, state, redirect_uri):
        self.states.append((state, redirect_uri))
        return f"https://exemplo.test/autorizar?state={state}"

    def exchange(self, code, redirect_uri):
        if self.error is not None:
            raise self.error
        return Authorization(identity=self.identity, access_token="token")

    def list_repos(self, access_token):
        return self.repos


def make_app(provider, allowed="alice"):
    database = Database(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    database.create_all()
    settings = Settings(
        storage_root="/tmp",
        database_url="sqlite+pysqlite:///:memory:",
        secret_key="test",
        github_allowed_users=allowed,
    )
    app = create_app(
        settings,
        database=database,
        users=UserRepository(database.session_factory),
        identity_provider=provider,
    )
    app.config.update(TESTING=True)
    return app


def test_config_is_public_and_decoupled_from_provider():
    body = make_app(FakeProvider()).test_client().get("/auth/config").get_json()
    assert body["provider"] == "fake"
    assert body["label"] == "Exemplo"
    assert body["login_url"] == "/auth/login"


def test_me_reports_unauthenticated():
    body = make_app(FakeProvider()).test_client().get("/auth/me").get_json()
    assert body == {"authenticated": False}


def test_login_redirects_to_provider_and_sets_state():
    provider = FakeProvider()
    client = make_app(provider).test_client()
    response = client.get("/auth/login")
    assert response.status_code == 302
    assert "exemplo.test" in response.headers["Location"]
    assert provider.states
    with client.session_transaction() as session:
        assert session["oauth_state"]


def test_callback_creates_session_for_allowed_identity():
    provider = FakeProvider(Identity(provider="fake", external_id="42", login="alice"))
    client = make_app(provider, allowed="alice, bob").test_client()
    client.get("/auth/login")
    with client.session_transaction() as session:
        state = session["oauth_state"]
    response = client.get(f"/auth/callback?code=abc&state={state}")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    assert client.get("/auth/me").get_json()["authenticated"] is True


def test_callback_denies_identity_outside_allowlist():
    provider = FakeProvider(Identity(provider="fake", external_id="7", login="mallory"))
    client = make_app(provider, allowed="alice").test_client()
    client.get("/auth/login")
    with client.session_transaction() as session:
        state = session["oauth_state"]
    response = client.get(f"/auth/callback?code=abc&state={state}")
    assert response.headers["Location"] == "/?auth=denied"
    assert client.get("/auth/me").get_json()["authenticated"] is False


def test_callback_rejects_state_mismatch():
    provider = FakeProvider(Identity(provider="fake", external_id="1", login="alice"))
    client = make_app(provider).test_client()
    client.get("/auth/login")
    response = client.get("/auth/callback?code=abc&state=tampered")
    assert response.headers["Location"] == "/?auth=invalid_state"


def test_callback_handles_provider_error():
    provider = FakeProvider(error=IdentityError("boom"))
    client = make_app(provider).test_client()
    client.get("/auth/login")
    with client.session_transaction() as session:
        state = session["oauth_state"]
    response = client.get(f"/auth/callback?code=abc&state={state}")
    assert response.headers["Location"] == "/?auth=error"


def test_logout_clears_session():
    provider = FakeProvider(Identity(provider="fake", external_id="1", login="alice"))
    client = make_app(provider).test_client()
    client.get("/auth/login")
    with client.session_transaction() as session:
        state = session["oauth_state"]
    client.get(f"/auth/callback?code=abc&state={state}")
    assert client.get("/auth/me").get_json()["authenticated"] is True
    client.get("/auth/logout")
    assert client.get("/auth/me").get_json()["authenticated"] is False


def test_me_exposes_profile():
    identity = Identity(
        provider="fake",
        external_id="1",
        login="alice",
        email="a@b.c",
        avatar_url="https://avatars.test/alice.png",
    )
    client = make_app(FakeProvider(identity)).test_client()
    client.get("/auth/login")
    with client.session_transaction() as session:
        state = session["oauth_state"]
    client.get(f"/auth/callback?code=abc&state={state}")
    user = client.get("/auth/me").get_json()["user"]
    assert user["login"] == "alice"
    assert user["email"] == "a@b.c"
    assert user["avatar_url"] == "https://avatars.test/alice.png"


def test_upsert_identity_is_idempotent():
    database = Database(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    database.create_all()
    users = UserRepository(database.session_factory)
    first = users.upsert_identity(Identity("fake", "1", "alice"))
    second = users.upsert_identity(Identity("fake", "1", "alice", email="a@b.c"))
    assert first.id == second.id
