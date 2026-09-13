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
