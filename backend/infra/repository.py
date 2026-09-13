from sqlalchemy import select

from .models import Project


class ProjectRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def create(self, owner_id: str, name: str, encoding: str = "windows-1252") -> Project:
        with self.session_factory() as session:
            project = Project(owner_id=owner_id, name=name, encoding=encoding)
            session.add(project)
            session.commit()
            return project

    def get(self, project_id):
        with self.session_factory() as session:
            return session.get(Project, project_id)

    def delete(self, project_id) -> None:
        with self.session_factory() as session:
            project = session.get(Project, project_id)
            if project is not None:
                session.delete(project)
                session.commit()

    def list_for_owner(self, owner_id: str) -> list[Project]:
        with self.session_factory() as session:
            statement = select(Project).where(Project.owner_id == owner_id)
            return list(session.scalars(statement))
