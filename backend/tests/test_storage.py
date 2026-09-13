import pytest

from infra.storage import (
    FilesystemStorage,
    PathTraversalError,
    StorageBackend,
    StorageError,
)


@pytest.fixture
def storage(tmp_path):
    return FilesystemStorage(tmp_path)


def test_write_then_read_roundtrip(storage):
    storage.create_project("local", "p1")
    storage.write_file("local", "p1", "texts/a.txt", b"conteudo")
    assert storage.read_file("local", "p1", "texts/a.txt") == b"conteudo"


def test_list_created_projects(storage):
    storage.create_project("local", "p1")
    storage.create_project("local", "p2")
    assert storage.list_projects("local") == ["p1", "p2"]


def test_list_files(storage):
    storage.create_project("local", "p1")
    storage.write_file("local", "p1", "texts/a.txt", b"a")
    storage.write_file("local", "p1", "texts/b.txt", b"b")
    storage.write_file("local", "p1", "fonts/f.NFTR", b"f")
    assert storage.list_files("local", "p1") == [
        "fonts/f.NFTR",
        "texts/a.txt",
        "texts/b.txt",
    ]


def test_list_files_missing_project_is_empty(storage):
    assert storage.list_files("local", "inexistente") == []


def test_path_traversal_rejected(storage, tmp_path):
    storage.create_project("local", "p1")
    with pytest.raises(PathTraversalError):
        storage.write_file("local", "p1", "../../escape.txt", b"x")
    assert not (tmp_path.parent / "escape.txt").exists()


def test_invalid_owner_segment_rejected(storage):
    with pytest.raises(StorageError):
        storage.create_project("../evil", "p1")


def test_delete_file(storage):
    storage.create_project("local", "p1")
    storage.write_file("local", "p1", "a.txt", b"x")
    storage.delete_file("local", "p1", "a.txt")
    with pytest.raises(FileNotFoundError):
        storage.read_file("local", "p1", "a.txt")


def test_is_storage_backend(storage):
    assert isinstance(storage, StorageBackend)
