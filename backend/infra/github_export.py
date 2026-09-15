import json
import urllib.error
import urllib.parse
import urllib.request

API_ROOT = "https://api.github.com"


class GitHubExportError(RuntimeError):
    pass


def _message(error) -> str:
    try:
        payload = json.loads(error.read().decode("utf-8"))
        if payload.get("message"):
            return str(payload["message"])
    except Exception:
        pass
    return f"falha ao consultar o GitHub ({getattr(error, 'code', 'erro')})"


class GitHubExportClient:
    def __init__(self, opener=None, api_root: str = API_ROOT):
        self._open = urllib.request.urlopen if opener is None else opener
        self.api_root = api_root

    def _request(self, method: str, path: str, token: str, payload=None, allow_404=False):
        data = None
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "previewer",
        }
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            self.api_root + path, data=data, headers=headers, method=method
        )
        try:
            with self._open(request) as response:
                raw = response.read()
        except urllib.error.HTTPError as error:
            if allow_404 and error.code == 404:
                return None
            raise GitHubExportError(_message(error)) from error
        except GitHubExportError:
            raise
        except Exception as error:
            raise GitHubExportError("falha ao consultar o GitHub") from error
        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except ValueError as error:
            raise GitHubExportError("resposta inválida do GitHub") from error

    def ensure_fork(self, *, upstream: str, login: str, token: str) -> str:
        head = f"{login}/{upstream.split('/')[-1]}"
        existing = self._request("GET", f"/repos/{head}", token, allow_404=True)
        if existing is None:
            self._request("POST", f"/repos/{upstream}/forks", token, payload={})
            return head
        if existing.get("full_name") == upstream:
            return head
        parent = (existing.get("parent") or {}).get("full_name")
        if not existing.get("fork") or parent != upstream:
            raise GitHubExportError(
                f"já existe um repositório {head!r} que não é um fork de {upstream!r}"
            )
        return head

    def merge_upstream(self, *, fork: str, branch: str, token: str):
        return self._request(
            "POST",
            f"/repos/{fork}/merge-upstream",
            token,
            payload={"branch": branch},
        )

    def compare(self, *, upstream: str, base: str, head: str, token: str):
        base_ref = urllib.parse.quote(base, safe="")
        head_ref = urllib.parse.quote(head, safe="")
        return self._request(
            "GET", f"/repos/{upstream}/compare/{base_ref}...{head_ref}", token
        )

    def create_pull(
        self, *, upstream: str, head: str, base: str, title: str, body: str, token: str
    ):
        return self._request(
            "POST",
            f"/repos/{upstream}/pulls",
            token,
            payload={"title": title, "head": head, "base": base, "body": body},
        )

    def find_pull(self, *, upstream: str, head: str, base: str, token: str):
        query = urllib.parse.urlencode({"head": head, "base": base, "state": "open"})
        pulls = self._request("GET", f"/repos/{upstream}/pulls?{query}", token)
        return pulls[0] if pulls else None

    def list_pulls(self, *, upstream: str, state: str, token: str):
        query = urllib.parse.urlencode({"state": state, "per_page": 100})
        return self._request("GET", f"/repos/{upstream}/pulls?{query}", token) or []

    def branch_has_manifest(self, *, repo: str, branch: str, token: str) -> bool:
        query = urllib.parse.urlencode({"ref": branch})
        return (
            self._request(
                "GET",
                f"/repos/{repo}/contents/manifest.json?{query}",
                token,
                allow_404=True,
            )
            is not None
        )

    def pull_state(self, *, upstream: str, number: int, token: str):
        return self._request("GET", f"/repos/{upstream}/pulls/{number}", token) or {}

    def pull_reviews(self, *, upstream: str, number: int, token: str):
        return (
            self._request(
                "GET", f"/repos/{upstream}/pulls/{number}/reviews", token
            )
            or []
        )

    def update_branch(self, *, upstream: str, number: int, token: str):
        return self._request(
            "PUT", f"/repos/{upstream}/pulls/{number}/update-branch", token, payload={}
        )

    def close_pull(self, *, upstream: str, number: int, token: str):
        return self._request(
            "PATCH",
            f"/repos/{upstream}/pulls/{number}",
            token,
            payload={"state": "closed"},
        )

    def delete_branch(self, *, repo: str, branch: str, token: str):
        ref = urllib.parse.quote(f"heads/{branch}", safe="")
        return self._request(
            "DELETE", f"/repos/{repo}/git/refs/{ref}", token, allow_404=True
        )
