import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

ROOT = Path(__file__).resolve().parents[1]
DATABASE_URL = os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL") or ""

pytestmark = pytest.mark.skipif(
    not DATABASE_URL.startswith("postgresql"),
    reason="requer Postgres via TEST_DATABASE_URL/DATABASE_URL",
)


def test_migrations_apply_to_postgres():
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "migrations"))
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    assert "projects" in inspect(engine).get_table_names()
