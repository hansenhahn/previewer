import pytest

from web.config import ConfigError, load_settings


def test_complete_config():
    settings = load_settings(
        {
            "STORAGE_ROOT": "/data",
            "DATABASE_URL": "sqlite+pysqlite:///:memory:",
            "SECRET_KEY": "segredo",
            "GITHUB_CLIENT_ID": "id",
            "GITHUB_CLIENT_SECRET": "secret",
            "GITHUB_ALLOWED_USERS": "alice",
        }
    )
    assert settings.storage_root == "/data"
    assert settings.secret_key == "segredo"
    assert settings.flask_env == "production"
    assert settings.github_client_id == "id"
    assert settings.github_allowed_users == "alice"


def test_missing_required_variable():
    with pytest.raises(ConfigError) as excinfo:
        load_settings({"STORAGE_ROOT": "/data", "DATABASE_URL": "sqlite+pysqlite://"})
    assert "SECRET_KEY" in str(excinfo.value)


def test_missing_github_credentials_fails_explicitly():
    with pytest.raises(ConfigError) as excinfo:
        load_settings(
            {
                "STORAGE_ROOT": "/data",
                "DATABASE_URL": "sqlite+pysqlite://",
                "SECRET_KEY": "segredo",
            }
        )
    assert "GITHUB_CLIENT_ID" in str(excinfo.value)


def test_secret_key_has_no_insecure_default():
    with pytest.raises(ConfigError):
        load_settings({"STORAGE_ROOT": "/data", "DATABASE_URL": "sqlite+pysqlite://"})
