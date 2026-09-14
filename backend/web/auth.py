import secrets
import uuid

from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    request,
    session,
    url_for,
)

from infra.github_import import refresh_repositories
from infra.identity import IdentityError, is_allowed, parse_allowlist

bp = Blueprint("auth", __name__, url_prefix="/auth")


def _settings():
    return current_app.config["SETTINGS"]


def _provider():
    return current_app.extensions["identity_provider"]


def _users():
    return current_app.extensions["users"]


def current_user():
    raw = session.get("user_id")
    if not raw:
        return None
    users = _users()
    if users is None:
        return None
    try:
        user_id = uuid.UUID(raw)
    except (ValueError, TypeError):
        return None
    return users.get(user_id)


def _redirect_uri() -> str:
    return url_for("auth.callback", _external=True)


def _refresh_repositories(user, access_token: str) -> None:
    store = current_app.extensions.get("repositories")
    provider = _provider()
    if store is None or not hasattr(provider, "list_repos"):
        return
    try:
        refresh_repositories(
            store=store, provider=provider, user_id=user.id, token=access_token
        )
    except Exception:
        current_app.logger.exception("falha ao atualizar repositórios no login")


@bp.get("/login")
def login():
    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state
    return redirect(_provider().login_url(state, _redirect_uri()))


@bp.get("/callback")
def callback():
    state = request.args.get("state")
    expected = session.pop("oauth_state", None)
    if not state or state != expected:
        return redirect("/?auth=invalid_state")
    code = request.args.get("code")
    if not code:
        return redirect("/?auth=denied")
    try:
        authorization = _provider().exchange(code, _redirect_uri())
    except IdentityError:
        return redirect("/?auth=error")
    identity = authorization.identity
    if not is_allowed(identity, parse_allowlist(_settings().github_allowed_users)):
        return redirect("/?auth=denied")
    user = _users().upsert_identity(identity, access_token=authorization.access_token)
    _refresh_repositories(user, authorization.access_token)
    session["user_id"] = str(user.id)
    return redirect("/")


@bp.get("/logout")
@bp.post("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("oauth_state", None)
    return redirect("/")


@bp.get("/config")
def config():
    provider = _provider()
    return jsonify(
        provider=provider.name,
        label=provider.label,
        login_url=url_for("auth.login"),
    )


@bp.get("/me")
def me():
    user = current_user()
    if user is None:
        return jsonify(authenticated=False)
    identity = _users().identity_for(user.id)
    return jsonify(
        authenticated=True,
        user={
            "id": str(user.id),
            "login": identity.login if identity else None,
            "email": identity.email if identity else None,
            "avatar_url": identity.avatar_url if identity else None,
        },
    )
