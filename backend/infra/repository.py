from datetime import datetime, timezone

from sqlalchemy import select

from .models import Change, Project, User, UserIdentity
from .models import UserRepository as UserRepositoryModel


class ProjectRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def create(
        self,
        owner_id: str,
        name: str,
        encoding: str = "windows-1252",
        project_id=None,
        upstream: str | None = None,
        base_branch: str | None = None,
    ) -> Project:
        with self.session_factory() as session:
            values = {
                "owner_id": owner_id,
                "name": name,
                "encoding": encoding,
                "upstream": upstream,
                "base_branch": base_branch,
            }
            if project_id is not None:
                values["id"] = project_id
            project = Project(**values)
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


class UserRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get(self, user_id) -> User | None:
        with self.session_factory() as session:
            return session.get(User, user_id)

    def identity_for(self, user_id) -> UserIdentity | None:
        with self.session_factory() as session:
            statement = (
                select(UserIdentity)
                .where(UserIdentity.user_id == user_id)
                .order_by(UserIdentity.created_at)
            )
            return session.scalars(statement).first()

    def access_token_for(self, user_id) -> str | None:
        identity = self.identity_for(user_id)
        return identity.access_token if identity else None

    def upsert_identity(self, identity, access_token: str | None = None) -> User:
        with self.session_factory() as session:
            statement = select(UserIdentity).where(
                UserIdentity.provider == identity.provider,
                UserIdentity.external_id == identity.external_id,
            )
            link = session.scalars(statement).first()
            if link is None:
                user = User()
                session.add(user)
                session.flush()
                session.add(
                    UserIdentity(
                        user_id=user.id,
                        provider=identity.provider,
                        external_id=identity.external_id,
                        login=identity.login,
                        email=identity.email,
                        avatar_url=identity.avatar_url,
                        access_token=access_token,
                    )
                )
            else:
                link.login = identity.login
                link.email = identity.email
                link.avatar_url = identity.avatar_url
                if access_token is not None:
                    link.access_token = access_token
                user = session.get(User, link.user_id)
            session.commit()
            return user


class ChangeRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def create(
        self,
        project_id,
        user_id,
        branch: str,
        title: str | None = None,
        base_commit: str | None = None,
        change_id=None,
        status: str = "draft",
        pr_number: int | None = None,
    ) -> Change:
        with self.session_factory() as session:
            values = {
                "project_id": project_id,
                "user_id": user_id,
                "branch": branch,
                "title": title,
                "base_commit": base_commit,
                "status": status,
                "pr_number": pr_number,
            }
            if change_id is not None:
                values["id"] = change_id
            change = Change(**values)
            session.add(change)
            session.commit()
            return change

    def get(self, change_id) -> Change | None:
        with self.session_factory() as session:
            return session.get(Change, change_id)

    def find(self, project_id, user_id, branch: str) -> Change | None:
        with self.session_factory() as session:
            statement = select(Change).where(
                Change.project_id == project_id,
                Change.user_id == user_id,
                Change.branch == branch,
            )
            return session.scalars(statement).first()

    def update(self, change_id, **fields) -> Change | None:
        with self.session_factory() as session:
            change = session.get(Change, change_id)
            if change is None:
                return None
            for key, value in fields.items():
                setattr(change, key, value)
            session.commit()
            return change

    def delete(self, change_id) -> None:
        with self.session_factory() as session:
            change = session.get(Change, change_id)
            if change is not None:
                session.delete(change)
                session.commit()

    def list_for_user(self, user_id, project_id=None) -> list[Change]:
        with self.session_factory() as session:
            statement = select(Change).where(Change.user_id == user_id)
            if project_id is not None:
                statement = statement.where(Change.project_id == project_id)
            statement = statement.order_by(Change.updated_at.desc())
            return list(session.scalars(statement))


class RepositoryStore:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def refresh(self, user_id, provider: str, repos) -> list[UserRepositoryModel]:
        with self.session_factory() as session:
            statement = select(UserRepositoryModel).where(
                UserRepositoryModel.user_id == user_id,
                UserRepositoryModel.provider == provider,
            )
            existing = {row.full_name: row for row in session.scalars(statement)}
            seen = set()
            for repo in repos:
                seen.add(repo.full_name)
                row = existing.get(repo.full_name)
                if row is None:
                    row = UserRepositoryModel(
                        user_id=user_id, provider=provider, full_name=repo.full_name
                    )
                    session.add(row)
                row.default_branch = repo.default_branch
                row.fork = repo.fork
            for full_name, row in existing.items():
                if full_name not in seen:
                    session.delete(row)
            session.commit()
            return self._list(session, user_id, provider)

    def find(self, user_id, full_name: str) -> UserRepositoryModel | None:
        with self.session_factory() as session:
            statement = select(UserRepositoryModel).where(
                UserRepositoryModel.user_id == user_id,
                UserRepositoryModel.full_name == full_name,
            )
            return session.scalars(statement).first()

    def list_for_user(self, user_id, provider: str | None = None) -> list[UserRepositoryModel]:
        with self.session_factory() as session:
            return self._list(session, user_id, provider)

    def record_checks(self, user_id, provider: str, checks: dict) -> None:
        now = datetime.now(timezone.utc)
        with self.session_factory() as session:
            statement = select(UserRepositoryModel).where(
                UserRepositoryModel.user_id == user_id,
                UserRepositoryModel.provider == provider,
            )
            for row in session.scalars(statement):
                if row.full_name not in checks:
                    continue
                ok, error = checks[row.full_name]
                row.manifest_ok = ok
                row.manifest_error = error
                row.checked_at = now
            session.commit()

    def _list(self, session, user_id, provider: str | None):
        statement = select(UserRepositoryModel).where(UserRepositoryModel.user_id == user_id)
        if provider is not None:
            statement = statement.where(UserRepositoryModel.provider == provider)
        statement = statement.order_by(UserRepositoryModel.full_name)
        return list(session.scalars(statement))
