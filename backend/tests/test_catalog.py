import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from infra.models import Base
from infra.repository import ProjectRepository


@pytest.fixture
def repository():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return ProjectRepository(sessionmaker(bind=engine, expire_on_commit=False))


def test_create_and_read_project(repository):
    project = repository.create("local", "meu-projeto", "windows-1252")
    fetched = repository.get(project.id)
    assert fetched.owner_id == "local"
    assert fetched.name == "meu-projeto"
    assert fetched.encoding == "windows-1252"
    assert fetched.created_at is not None
    assert fetched.updated_at is not None


def test_duplicate_name_same_owner_rejected(repository):
    repository.create("local", "dup")
    with pytest.raises(IntegrityError):
        repository.create("local", "dup")


def test_same_name_other_owner_allowed(repository):
    repository.create("local", "dup")
    repository.create("outro", "dup")
    assert len(repository.list_for_owner("outro")) == 1


def test_owner_associated(repository):
    project = repository.create("alice", "p")
    assert project.owner_id == "alice"


def test_create_stores_upstream_and_base_branch(repository):
    project = repository.create(
        "alice",
        "p",
        upstream="upstream/projeto",
        base_branch="main",
    )
    fetched = repository.get(project.id)
    assert fetched.upstream == "upstream/projeto"
    assert fetched.base_branch == "main"
