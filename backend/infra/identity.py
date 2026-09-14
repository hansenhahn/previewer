from dataclasses import dataclass
from typing import Protocol


class IdentityError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class Identity:
    provider: str
    external_id: str
    login: str
    email: str | None = None
    avatar_url: str | None = None


@dataclass(frozen=True, slots=True)
class Authorization:
    identity: Identity
    access_token: str


@dataclass(frozen=True, slots=True)
class RepositoryRef:
    provider: str
    full_name: str
    default_branch: str
    fork: bool
    private: bool = False


class IdentityProvider(Protocol):
    name: str
    label: str

    def login_url(self, state: str, redirect_uri: str) -> str: ...

    def exchange(self, code: str, redirect_uri: str) -> Authorization: ...

    def list_repos(self, access_token: str) -> list[RepositoryRef]: ...


def parse_allowlist(raw: str) -> set[str]:
    return {value.strip().lower() for value in (raw or "").split(",") if value.strip()}


def is_allowed(identity: Identity, allowed: set[str]) -> bool:
    return identity.login.lower() in allowed
