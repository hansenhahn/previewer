from flask import Flask

from .config import Settings


def create_app(
    settings: Settings,
    database=None,
    storage=None,
    projects=None,
    users=None,
    identity_provider=None,
    repositories=None,
    github_source=None,
) -> Flask:
    app = Flask(__name__)
    app.config.update(SECRET_KEY=settings.secret_key, SETTINGS=settings)

    if database is None:
        from infra.db import Database

        database = Database(settings.database_url)
    app.extensions["database"] = database

    if storage is None:
        from infra.storage import FilesystemStorage

        storage = FilesystemStorage(settings.storage_root)
    app.extensions["storage"] = storage

    session_factory = getattr(database, "session_factory", None)

    if projects is None and session_factory is not None:
        from infra.repository import ProjectRepository

        projects = ProjectRepository(session_factory)
    app.extensions["projects"] = projects

    if users is None and session_factory is not None:
        from infra.repository import UserRepository

        users = UserRepository(session_factory)
    app.extensions["users"] = users

    if repositories is None and session_factory is not None:
        from infra.repository import RepositoryStore

        repositories = RepositoryStore(session_factory)
    app.extensions["repositories"] = repositories

    if identity_provider is None:
        from infra.github import GitHubOAuthProvider

        identity_provider = GitHubOAuthProvider(
            settings.github_client_id, settings.github_client_secret
        )
    app.extensions["identity_provider"] = identity_provider

    if github_source is None:
        from infra.github_source import GitHubSource

        github_source = GitHubSource()
    app.extensions["github_source"] = github_source

    from .routes import bp

    app.register_blueprint(bp)

    from .auth import bp as auth_bp

    app.register_blueprint(auth_bp)

    from .api import bp as api_bp

    app.register_blueprint(api_bp)

    return app
