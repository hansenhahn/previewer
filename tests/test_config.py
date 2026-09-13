import pytest

from app.config import ConfigError, load_settings


def test_complete_config():
    settings = load_settings(
        {
            "STORAGE_ROOT": "/data",
            "DATABASE_URL": "sqlite+pysqlite:///:memory:",
            "SECRET_KEY": "segredo",
        }
    )
    assert settings.storage_root == "/data"
    assert settings.secret_key == "segredo"
    assert settings.flask_env == "production"


def test_missing_required_variable():
    with pytest.raises(ConfigError) as excinfo:
        load_settings({"STORAGE_ROOT": "/data", "DATABASE_URL": "sqlite+pysqlite://"})
    assert "SECRET_KEY" in str(excinfo.value)


def test_secret_key_has_no_insecure_default():
    with pytest.raises(ConfigError):
        load_settings({"STORAGE_ROOT": "/data", "DATABASE_URL": "sqlite+pysqlite://"})
