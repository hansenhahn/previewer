from flask import Flask

from .config import Settings


def create_app(settings: Settings, database=None, storage=None, projects=None) -> Flask:
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

    if projects is None:
        session_factory = getattr(database, "session_factory", None)
        if session_factory is not None:
            from infra.repository import ProjectRepository

            projects = ProjectRepository(session_factory)
    app.extensions["projects"] = projects

    from .routes import bp

    app.register_blueprint(bp)

    from .api import bp as api_bp

    app.register_blueprint(api_bp)

    return app
