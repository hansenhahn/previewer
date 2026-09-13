import io
import zipfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from infra.ingestion import (
    InvalidBundleError,
    ProjectNameConflict,
    import_bundle,
)
from infra.models import Base
from infra.repository import ProjectRepository
from infra.storage import FilesystemStorage
from tests.fixtures.project import build_bundle, manifest_document


@pytest.fixture
def repository():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return ProjectRepository(sessionmaker(bind=engine, expire_on_commit=False))


@pytest.fixture
def storage(tmp_path):
    return FilesystemStorage(tmp_path)


def test_import_success(repository, storage):
    project, manifest = import_bundle(
        storage=storage, repository=repository, owner_id="local", data=build_bundle()
    )
    assert project.name == "Meu Projeto"
    assert manifest.encoding == "windows-1252"
    files = storage.list_files("local", str(project.id))
    assert "manifest.json" in files
    assert "texts/cap01.txt" in files
    assert "fonts/fontevent.NFTR" in files


def test_import_rejects_missing_manifest(repository, storage):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("texts/cap01.txt", b"texto")
    with pytest.raises(InvalidBundleError):
        import_bundle(
            storage=storage,
            repository=repository,
            owner_id="local",
            data=buffer.getvalue(),
        )
    assert repository.list_for_owner("local") == []


def test_import_rejects_path_traversal(repository, storage, tmp_path):
    bundle = build_bundle(extra_members={"../escape.txt": b"x"})
    with pytest.raises(InvalidBundleError):
        import_bundle(
            storage=storage, repository=repository, owner_id="local", data=bundle
        )
    assert not (tmp_path.parent / "escape.txt").exists()
    assert repository.list_for_owner("local") == []


def test_import_rejects_duplicate_name(repository, storage):
    import_bundle(
        storage=storage, repository=repository, owner_id="local", data=build_bundle()
    )
    with pytest.raises(ProjectNameConflict):
        import_bundle(
            storage=storage,
            repository=repository,
            owner_id="local",
            data=build_bundle(),
        )
    assert len(repository.list_for_owner("local")) == 1


def test_import_rejects_missing_referenced_file(repository, storage):
    document = manifest_document(font_path="fonts/ausente.NFTR")
    with pytest.raises(InvalidBundleError):
        import_bundle(
            storage=storage,
            repository=repository,
            owner_id="local",
            data=build_bundle(document),
        )
    assert repository.list_for_owner("local") == []
