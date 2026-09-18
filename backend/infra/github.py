import json
import urllib.parse
import urllib.request

from .identity import Authorization, Identity, IdentityError, RepositoryRef

AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"
API_ROOT = "https://api.github.com"
SCOPES = "read:user user:email repo"


def _secure_avatar(url) -> str | None:
    if isinstance(url, str) and url.startswith("https://"):
        return url
    return None


class GitHubOAuthProvider:
    name = "github"
    label = "GitHub"

    def __init__(self, client_id: str, client_secret: str, opener=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self._open = urllib.request.urlopen if opener is None else opener

    def login_url(self, state: str, redirect_uri: str) -> str:
        query = urllib.parse.urlencode(
            {
                "client_id": self.client_id,
                "redirect_uri": redirect_uri,
                "scope": SCOPES,
                "state": state,
                "allow_signup": "false",
            }
        )
        return f"{AUTHORIZE_URL}?{query}"

    def exchange(self, code: str, redirect_uri: str) -> Authorization:
        token = self._access_token(code, redirect_uri)
        profile = self._api_get("/user", token)
        email = profile.get("email")
        if not email:
            emails = self._api_get("/user/emails", token)
            primary = next((item for item in emails if item.get("primary")), None)
            email = (primary or {}).get("email")
        identity = Identity(
            provider=self.name,
            external_id=str(profile["id"]),
            login=profile["login"],
            email=email,
            avatar_url=_secure_avatar(profile.get("avatar_url")),
        )
        return Authorization(identity=identity, access_token=token)

    def list_repos(self, access_token: str) -> list[RepositoryRef]:
        repos: list[RepositoryRef] = []
        page = 1
        while True:
            batch = self._api_get(
                f"/user/repos?per_page=100&affiliation=owner&sort=updated&page={page}",
                access_token,
            )
            if not batch:
                break
            for repo in batch:
                repos.append(
                    RepositoryRef(
                        provider=self.name,
                        full_name=repo["full_name"],
                        default_branch=repo.get("default_branch") or "main",
                        fork=bool(repo.get("fork")),
                        private=bool(repo.get("private")),
                    )
                )
            if len(batch) < 100:
                break
            page += 1
        return repos

    def get_repo(self, full_name: str, access_token: str) -> dict:
        return self._api_get(f"/repos/{full_name}", access_token)

    def _access_token(self, code: str, redirect_uri: str) -> str:
        data = urllib.parse.urlencode(
            {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            TOKEN_URL, data=data, headers={"Accept": "application/json"}
        )
        payload = self._read_json(request)
        token = payload.get("access_token")
        if not token:
            raise IdentityError("não foi possível obter o token de acesso")
        return token

    def _api_get(self, path: str, token: str):
        request = urllib.request.Request(
            API_ROOT + path,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "previewer",
            },
        )
        return self._read_json(request)

    def _read_json(self, request):
        try:
            with self._open(request) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as error:
            raise IdentityError("falha ao consultar o GitHub") from error
