import os
from dataclasses import dataclass


class ConfigError(RuntimeError):
    pass


REQUIRED = (
    "STORAGE_ROOT",
    "DATABASE_URL",
    "SECRET_KEY",
    "GITHUB_CLIENT_ID",
    "GITHUB_CLIENT_SECRET",
    "GITHUB_ALLOWED_USERS",
)


@dataclass(frozen=True, slots=True)
class Settings:
    storage_root: str
    database_url: str
    secret_key: str
    flask_env: str = "production"
    github_client_id: str = ""
    github_client_secret: str = ""
    github_allowed_users: str = ""


def load_settings(environ=None) -> Settings:
    environ = os.environ if environ is None else environ
    missing = [name for name in REQUIRED if not environ.get(name)]
    if missing:
        raise ConfigError(
            "variáveis de ambiente obrigatórias ausentes: " + ", ".join(missing)
        )
    return Settings(
        storage_root=environ["STORAGE_ROOT"],
        database_url=environ["DATABASE_URL"],
        secret_key=environ["SECRET_KEY"],
        flask_env=environ.get("FLASK_ENV", "production"),
        github_client_id=environ["GITHUB_CLIENT_ID"],
        github_client_secret=environ["GITHUB_CLIENT_SECRET"],
        github_allowed_users=environ["GITHUB_ALLOWED_USERS"],
    )
