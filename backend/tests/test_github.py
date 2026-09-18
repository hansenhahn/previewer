import json

from infra.github import GitHubOAuthProvider


class FakeResponse:
    def __init__(self, payload):
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def opener(routes):
    def _open(request):
        for fragment, payload in routes.items():
            if fragment in request.full_url:
                return FakeResponse(payload)
        raise AssertionError(f"URL inesperada: {request.full_url}")

    return _open


def test_login_url_requests_identity_and_write_scopes():
    provider = GitHubOAuthProvider("id", "secret")
    url = provider.login_url("estado", "https://app.test/auth/callback")
    assert url.startswith("https://github.com/login/oauth/authorize?")
    assert "scope=read%3Auser+user%3Aemail+repo" in url
    assert "state=estado" in url
    assert "redirect_uri=https%3A%2F%2Fapp.test%2Fauth%2Fcallback" in url
    assert "scope=public_repo" not in url


def test_exchange_reads_profile_and_primary_email():
    provider = GitHubOAuthProvider(
        "id",
        "secret",
        opener=opener(
            {
                "/login/oauth/access_token": {"access_token": "tok"},
                "/user/emails": [
                    {"email": "secundario@b.c", "primary": False},
                    {"email": "alice@b.c", "primary": True},
                ],
                "/user": {"id": 7, "login": "alice", "avatar_url": "https://a/x.png"},
            }
        ),
    )
    authorization = provider.exchange("code", "https://app.test/auth/callback")
    identity = authorization.identity
    assert authorization.access_token == "tok"
    assert identity.provider == "github"
    assert identity.external_id == "7"
    assert identity.login == "alice"
    assert identity.email == "alice@b.c"
    assert identity.avatar_url == "https://a/x.png"


def test_exchange_rejects_insecure_avatar():
    provider = GitHubOAuthProvider(
        "id",
        "secret",
        opener=opener(
            {
                "/login/oauth/access_token": {"access_token": "tok"},
                "/user": {
                    "id": 7,
                    "login": "alice",
                    "email": "alice@b.c",
                    "avatar_url": "http://inseguro/x.png",
                },
            }
        ),
    )
    authorization = provider.exchange("code", "https://app.test/auth/callback")
    assert authorization.identity.avatar_url is None


def test_get_repo_reads_parent():
    provider = GitHubOAuthProvider(
        "id",
        "secret",
        opener=opener(
            {
                "/repos/alice/projeto": {
                    "full_name": "alice/projeto",
                    "fork": True,
                    "default_branch": "main",
                    "parent": {"full_name": "upstream/projeto", "default_branch": "main"},
                }
            }
        ),
    )
    meta = provider.get_repo("alice/projeto", "tok")
    assert meta["parent"]["full_name"] == "upstream/projeto"


def test_list_repos_includes_private():
    provider = GitHubOAuthProvider(
        "id",
        "secret",
        opener=opener(
            {
                "/user/repos": [
                    {
                        "full_name": "alice/projeto",
                        "default_branch": "main",
                        "fork": False,
                        "private": False,
                    },
                    {
                        "full_name": "alice/segredo",
                        "default_branch": "main",
                        "fork": False,
                        "private": True,
                    },
                    {
                        "full_name": "alice/fork-do-projeto",
                        "default_branch": "translation",
                        "fork": True,
                        "private": False,
                    },
                ]
            }
        ),
    )
    repos = provider.list_repos("tok")
    assert [repo.full_name for repo in repos] == [
        "alice/projeto",
        "alice/segredo",
        "alice/fork-do-projeto",
    ]
    assert repos[0].default_branch == "main"
    assert repos[1].private is True
    assert repos[2].fork is True
