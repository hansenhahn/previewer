import pytest

from infra.db import Database


def test_health_sqlite():
    database = Database("sqlite+pysqlite:///:memory:")
    assert database.is_healthy() is True


def test_health_unreachable_database():
    database = Database("sqlite+pysqlite:////diretorio-inexistente-xyz/db.sqlite")
    assert database.is_healthy() is False
