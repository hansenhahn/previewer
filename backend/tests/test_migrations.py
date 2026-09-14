from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

ROOT = Path(__file__).resolve().parents[1]


def _config(db_path: Path) -> Config:
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "migrations"))
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{db_path}")
    return config


def test_upgrade_creates_projects_table(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    db_path = tmp_path / "empty.sqlite"
    command.upgrade(_config(db_path), "head")
    engine = create_engine(f"sqlite+pysqlite:///{db_path}")
    assert "projects" in inspect(engine).get_table_names()


def test_upgrade_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    db_path = tmp_path / "twice.sqlite"
    config = _config(db_path)
    command.upgrade(config, "head")
    command.upgrade(config, "head")
    engine = create_engine(f"sqlite+pysqlite:///{db_path}")
    assert "projects" in inspect(engine).get_table_names()


def test_upgrade_adds_avatar_column(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    db_path = tmp_path / "avatar.sqlite"
    command.upgrade(_config(db_path), "head")
    engine = create_engine(f"sqlite+pysqlite:///{db_path}")
    columns = {column["name"] for column in inspect(engine).get_columns("user_identities")}
    assert "avatar_url" in columns


def test_upgrade_adds_token_and_manifest_columns(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    db_path = tmp_path / "token.sqlite"
    command.upgrade(_config(db_path), "head")
    engine = create_engine(f"sqlite+pysqlite:///{db_path}")
    identity_columns = {
        column["name"] for column in inspect(engine).get_columns("user_identities")
    }
    repository_columns = {
        column["name"] for column in inspect(engine).get_columns("user_repositories")
    }
    assert "access_token" in identity_columns
    assert {"manifest_ok", "manifest_error", "checked_at"} <= repository_columns
