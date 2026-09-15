import uuid

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool

from infra.db import Database
from infra.identity import Identity
from infra.repository import ChangeRepository, ProjectRepository, UserRepository


@pytest.fixture
def repos():
    database = Database(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    database.create_all()
    users = UserRepository(database.session_factory)
    user = users.upsert_identity(Identity("github", "1", "alice"))
    projects = ProjectRepository(database.session_factory)
    project = projects.create(str(user.id), "Projeto")
    return user, project, ChangeRepository(database.session_factory)


def test_create_and_find(repos):
    user, project, changes = repos
    change = changes.create(project.id, user.id, "previewer/abc", title="Título")
    assert change.status == "draft"
    assert change.pr_number is None
    assert changes.get(change.id).branch == "previewer/abc"
    found = changes.find(project.id, user.id, "previewer/abc")
    assert found is not None
    assert found.id == change.id
    assert changes.find(project.id, user.id, "previewer/outra") is None


def test_branch_is_unique_per_project_and_user(repos):
    user, project, changes = repos
    changes.create(project.id, user.id, "previewer/abc")
    with pytest.raises(IntegrityError):
        changes.create(project.id, user.id, "previewer/abc")


def test_update_fields(repos):
    user, project, changes = repos
    change = changes.create(project.id, user.id, "previewer/abc")
    updated = changes.update(change.id, status="open", pr_number=7, title="Pronto")
    assert updated.status == "open"
    assert updated.pr_number == 7
    assert updated.title == "Pronto"
    assert changes.update(uuid.uuid4(), status="open") is None


def test_list_for_user_filters_by_project(repos):
    user, project, changes = repos
    changes.create(project.id, user.id, "previewer/a")
    changes.create(project.id, user.id, "previewer/b")
    assert len(changes.list_for_user(user.id)) == 2
    assert len(changes.list_for_user(user.id, project.id)) == 2
    assert changes.list_for_user(uuid.uuid4()) == []


def test_delete(repos):
    user, project, changes = repos
    change = changes.create(project.id, user.id, "previewer/abc")
    changes.delete(change.id)
    assert changes.get(change.id) is None
