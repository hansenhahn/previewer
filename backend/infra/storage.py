from pathlib import Path
from typing import Protocol, runtime_checkable


class StorageError(RuntimeError):
    pass


class PathTraversalError(StorageError):
    pass


@runtime_checkable
class StorageBackend(Protocol):
    def create_project(self, owner_id: str, project_id: str) -> None: ...

    def list_projects(self, owner_id: str) -> list[str]: ...

    def list_files(self, owner_id: str, project_id: str) -> list[str]: ...

    def write_file(
        self, owner_id: str, project_id: str, relative_path: str, data: bytes
    ) -> None: ...

    def read_file(self, owner_id: str, project_id: str, relative_path: str) -> bytes: ...

    def delete_file(
        self, owner_id: str, project_id: str, relative_path: str
    ) -> None: ...


def _segment(value: str, label: str) -> str:
    text = str(value)
    if not text or text in (".", "..") or "/" in text or "\\" in text or "\x00" in text:
        raise StorageError(f"{label} inválido: {value!r}")
    return text


class FilesystemStorage:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _owner_dir(self, owner_id: str) -> Path:
        return self.root / _segment(owner_id, "owner_id")

    def _project_dir(self, owner_id: str, project_id: str) -> Path:
        return self._owner_dir(owner_id) / _segment(project_id, "project_id")

    def _resolve(self, base: Path, relative_path: str) -> Path:
        base_resolved = base.resolve()
        candidate = (base_resolved / relative_path).resolve()
        if not candidate.is_relative_to(self.root) or not candidate.is_relative_to(
            base_resolved
        ):
            raise PathTraversalError(f"caminho fora da raiz: {relative_path!r}")
        return candidate

    def create_project(self, owner_id: str, project_id: str) -> None:
        self._project_dir(owner_id, project_id).mkdir(parents=True, exist_ok=True)

    def list_projects(self, owner_id: str) -> list[str]:
        owner_dir = self._owner_dir(owner_id)
        if not owner_dir.is_dir():
            return []
        return sorted(entry.name for entry in owner_dir.iterdir() if entry.is_dir())

    def list_files(self, owner_id: str, project_id: str) -> list[str]:
        base = self._project_dir(owner_id, project_id)
        if not base.is_dir():
            return []
        files = [
            path.relative_to(base).as_posix()
            for path in base.rglob("*")
            if path.is_file() and not path.is_symlink()
        ]
        return sorted(files)

    def write_file(
        self, owner_id: str, project_id: str, relative_path: str, data: bytes
    ) -> None:
        target = self._resolve(self._project_dir(owner_id, project_id), relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def read_file(self, owner_id: str, project_id: str, relative_path: str) -> bytes:
        target = self._resolve(self._project_dir(owner_id, project_id), relative_path)
        return target.read_bytes()

    def delete_file(self, owner_id: str, project_id: str, relative_path: str) -> None:
        target = self._resolve(self._project_dir(owner_id, project_id), relative_path)
        target.unlink()
