import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .git import GitError, GitWorkspace
from .github_export import GitHubExportClient, GitHubExportError

FULL_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*$")
GITHUB_URL = re.compile(
    r"github\.com[:/]+([A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*?)(?:\.git)?/?$"
)
PUBLISHED_REF = "refs/previewer/published"
SCRATCH_REF = "refs/previewer/scratch"
CHANGE_PREFIX = "previewer/"
EPHEMERAL_BRANCH = CHANGE_PREFIX + "sketch"


class ProjectExportError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class PublishResult:
    pr_number: int
    url: str
    created: bool
    branch: str


@dataclass(frozen=True, slots=True)
class PullState:
    state: str
    merged: bool
    changes_requested: bool


@dataclass(frozen=True, slots=True)
class PullRef:
    number: int
    branch: str
    title: str
    resumable: bool = True


@runtime_checkable
class ProjectExport(Protocol):
    def origin_remote(self, *, workspace) -> str | None: ...

    def default_branch(self, *, workspace) -> str: ...

    def current_branch(self, *, workspace) -> str: ...

    def branch_exists(self, *, workspace, branch: str) -> bool: ...

    def ensure_branch(self, *, workspace, branch: str, base: str) -> None: ...

    def checkout_base(self, *, workspace, base: str) -> None: ...

    def backup(self, *, workspace, repo: str, branch: str, token: str) -> None: ...

    def commit(self, *, workspace, branch: str, base: str, message: str) -> None: ...

    def has_uncommitted(self, *, workspace) -> bool: ...

    def has_unpushed(self, *, workspace, branch: str, base: str) -> bool: ...

    def restore(self, *, workspace, branch: str, base: str) -> None: ...

    def resume(self, *, workspace, branch: str, base: str) -> None: ...

    def abandon(self, *, workspace, branch: str, base: str) -> None: ...

    def ensure_fork(
        self, *, upstream: str, login: str, token: str, base: str
    ) -> str: ...

    def sync(
        self, *, workspace, upstream: str, base: str, branch: str, token: str
    ) -> bool: ...

    def publish(
        self,
        *,
        workspace,
        upstream: str,
        base: str,
        branch: str,
        login: str,
        token: str,
        title: str,
        body: str,
        target_branch: str | None = None,
    ) -> PublishResult: ...

    def pr_status(self, *, upstream: str, number: int, token: str) -> PullState: ...

    def open_pulls(
        self, *, upstream: str, head_repo: str, token: str
    ) -> list[PullRef]: ...

    def close_pull(self, *, upstream: str, number: int, token: str) -> None: ...

    def delete_remote_branch(self, *, repo: str, branch: str, token: str) -> None: ...


def backup_branch(branch: str) -> str:
    stem = branch[len("previewer/") :] if branch.startswith("previewer/") else branch
    return f"previewer-backup/{stem}"


def parse_upstream(url: str) -> str | None:
    match = GITHUB_URL.search(url or "")
    if not match:
        return None
    candidate = match.group(1)
    return candidate if FULL_NAME.match(candidate) else None


def _push_error(error: GitError) -> GitHubExportError:
    message = str(error)
    lowered = message.lower()
    if "403" in message or "denied" in lowered or "permission" in lowered:
        return GitHubExportError(
            "sua credencial do GitHub não tem permissão de escrita; "
            "saia e entre novamente para autorizar (escopo public_repo)"
        )
    return GitHubExportError(message)


def _changes_requested(reviews) -> bool:
    latest: dict[str, str] = {}
    for review in reviews:
        state = review.get("state")
        if state in ("APPROVED", "CHANGES_REQUESTED"):
            login = (review.get("user") or {}).get("login", "")
            latest[login] = state
    return any(state == "CHANGES_REQUESTED" for state in latest.values())


class GitHubProjectExport:
    def __init__(self, client=None, *, allow_file: bool = False, timeout: int = 180):
        self.client = client or GitHubExportClient()
        self.allow_file = allow_file
        self.timeout = timeout

    def _fork_url(self, fork: str, token: str) -> str:
        return f"https://x-access-token:{token}@github.com/{fork}.git"

    def _upstream_url(self, upstream: str, token: str) -> str:
        return f"https://github.com/{upstream}.git"

    def _git(self, workspace, token: str | None = None) -> GitWorkspace:
        return GitWorkspace(
            workspace,
            allow_file=self.allow_file,
            timeout=self.timeout,
            secrets=(token,) if token else (),
        )

    def _reference_exists(self, git: GitWorkspace, reference: str) -> bool:
        return git.returncode("show-ref", "--verify", "--quiet", reference) == 0

    def _count(self, git: GitWorkspace, revision_range: str) -> int:
        try:
            output = git.run(
                "rev-list", "--count", revision_range, capture=True
            ).decode()
        except GitError:
            return 0
        try:
            return int(output.strip())
        except ValueError:
            return 0

    def origin_remote(self, *, workspace) -> str | None:
        try:
            url = self._git(workspace).run(
                "remote", "get-url", "origin", capture=True
            )
        except GitError:
            return None
        return parse_upstream(url.decode("utf-8", "replace").strip())

    def default_branch(self, *, workspace) -> str:
        git = self._git(workspace)
        try:
            ref = git.run(
                "symbolic-ref", "--short", "refs/remotes/origin/HEAD", capture=True
            )
            name = ref.decode().strip()
            if "/" in name:
                return name.split("/", 1)[1]
        except GitError:
            pass
        for candidate in ("main", "master"):
            if self._reference_exists(git, f"refs/remotes/origin/{candidate}"):
                return candidate
        return "main"

    def current_branch(self, *, workspace) -> str:
        return (
            self._git(workspace)
            .run("rev-parse", "--abbrev-ref", "HEAD", capture=True)
            .decode()
            .strip()
        )

    def branch_exists(self, *, workspace, branch: str) -> bool:
        return self._reference_exists(
            self._git(workspace), f"refs/heads/{branch}"
        )

    def _switch_base(self, git: GitWorkspace, base: str) -> None:
        if self._reference_exists(git, f"refs/heads/{base}"):
            git.run("switch", base)
        else:
            git.run("switch", "-c", base, f"origin/{base}")

    def ensure_branch(self, *, workspace, branch: str, base: str) -> None:
        git = self._git(workspace)
        if self._reference_exists(git, f"refs/heads/{branch}"):
            if git.run(
                "rev-parse", "--abbrev-ref", "HEAD", capture=True
            ).decode().strip() != branch:
                git.run("switch", branch)
            return
        try:
            git.run("fetch", "origin", base)
        except GitError:
            pass
        start = f"origin/{base}"
        if not self._reference_exists(git, f"refs/remotes/origin/{base}"):
            start = base
        git.run("switch", "-c", branch, start)

    def checkout_base(self, *, workspace, base: str) -> None:
        git = self._git(workspace)
        try:
            git.run("fetch", "origin", base)
        except GitError:
            pass
        self._switch_base(git, base)
        if self._reference_exists(git, f"refs/remotes/origin/{base}"):
            git.run("reset", "--hard", f"origin/{base}")

    def backup(self, *, workspace, repo: str, branch: str, token: str) -> None:
        git = self._git(workspace, token)
        current = git.run("rev-parse", "--abbrev-ref", "HEAD", capture=True).decode().strip()
        if current != branch:
            git.run("switch", branch)
        target = backup_branch(branch)
        try:
            git.run("push", self._fork_url(repo, token), f"{branch}:refs/heads/{target}")
        except GitError as error:
            raise _push_error(error) from error

    def commit(self, *, workspace, branch: str, base: str, message: str) -> None:
        git = self._git(workspace)
        current = git.run("rev-parse", "--abbrev-ref", "HEAD", capture=True).decode().strip()
        if current != branch:
            git.run("switch", branch)
        git.run("add", "-A")
        if git.returncode("diff", "--cached", "--quiet") == 0:
            return
        git.run("commit", "-m", message)

    def _squash(self, git: GitWorkspace, *, branch: str, base: str, message: str) -> None:
        published = f"{PUBLISHED_REF}/{branch}"
        target = published if self._reference_exists(git, published) else f"origin/{base}"
        if self._count(git, f"{target}..HEAD") == 0:
            return
        git.run("update-ref", f"{SCRATCH_REF}/{branch}", "HEAD")
        git.run("reset", "--soft", target)
        git.run("commit", "-m", message)

    def has_uncommitted(self, *, workspace) -> bool:
        return bool(
            self._git(workspace)
            .run("status", "--porcelain", capture=True)
            .strip()
        )

    def has_unpushed(self, *, workspace, branch: str, base: str) -> bool:
        git = self._git(workspace)
        if self.has_uncommitted(workspace=workspace):
            return True
        published = f"{PUBLISHED_REF}/{branch}"
        if self._reference_exists(git, published):
            return self._count(git, f"{published}..HEAD") > 0
        if not self._reference_exists(git, f"refs/remotes/origin/{base}"):
            return False
        return self._count(git, f"origin/{base}..HEAD") > 0

    def restore(self, *, workspace, branch: str, base: str) -> None:
        git = self._git(workspace)
        if git.run("rev-parse", "--abbrev-ref", "HEAD", capture=True).decode().strip() != branch:
            git.run("switch", branch)
        published = f"{PUBLISHED_REF}/{branch}"
        if self._reference_exists(git, published):
            target = published
        elif self._reference_exists(git, f"refs/remotes/origin/{base}"):
            target = f"origin/{base}"
        else:
            target = "HEAD"
        git.run("reset", "--hard", target)
        scratch = f"{SCRATCH_REF}/{branch}"
        if self._reference_exists(git, scratch):
            git.run("update-ref", "-d", scratch)

    def resume(self, *, workspace, branch: str, base: str) -> None:
        git = self._git(workspace)
        current = git.run("rev-parse", "--abbrev-ref", "HEAD", capture=True).decode().strip()
        if current == branch:
            return
        if current.startswith("previewer/") and self.has_uncommitted(
            workspace=workspace
        ):
            raise ProjectExportError(
                "há edições não salvas; salve ou descarte antes de trocar"
            )
        if not self._reference_exists(git, f"refs/heads/{branch}"):
            try:
                git.run("fetch", "origin", f"{branch}:{branch}")
            except GitError as error:
                raise ProjectExportError(
                    "não foi possível carregar essa alteração"
                ) from error
        git.run("switch", branch)

    def abandon(self, *, workspace, branch: str, base: str) -> None:
        git = self._git(workspace)
        switched = (
            git.run("rev-parse", "--abbrev-ref", "HEAD", capture=True).decode().strip()
            == branch
        )
        if switched:
            self._switch_base(git, base)
            try:
                git.run("fetch", "origin", base)
                if self._reference_exists(git, f"refs/remotes/origin/{base}"):
                    git.run("reset", "--hard", f"origin/{base}")
            except GitError:
                pass
        if self._reference_exists(git, f"refs/heads/{branch}"):
            git.run("branch", "-D", branch)
        published = f"{PUBLISHED_REF}/{branch}"
        if self._reference_exists(git, published):
            git.run("update-ref", "-d", published)
        scratch = f"{SCRATCH_REF}/{branch}"
        if self._reference_exists(git, scratch):
            git.run("update-ref", "-d", scratch)

    def ensure_fork(self, *, upstream: str, login: str, token: str, base: str) -> str:
        fork = self.client.ensure_fork(upstream=upstream, login=login, token=token)
        try:
            self.client.merge_upstream(fork=fork, branch=base, token=token)
        except GitHubExportError:
            pass
        return fork

    def sync(
        self, *, workspace, upstream: str, base: str, branch: str, token: str
    ) -> bool:
        git = self._git(workspace, token)
        remotes = git.run("remote", capture=True).decode().split()
        if "upstream" not in remotes:
            git.run("remote", "add", "upstream", self._upstream_url(upstream, token))
        git.run("fetch", "upstream", base)
        behind = self._count(git, f"HEAD..upstream/{base}") > 0
        if behind:
            git.run("merge", "--no-edit", f"upstream/{base}")
        return behind

    def publish(
        self,
        *,
        workspace,
        upstream: str,
        base: str,
        branch: str,
        login: str,
        token: str,
        title: str,
        body: str,
        target_branch: str | None = None,
    ) -> PublishResult:
        git = self._git(workspace, token)
        fork = self.ensure_fork(
            upstream=upstream, login=login, token=token, base=base
        )
        self.commit(
            workspace=workspace, branch=branch, base=base, message=title
        )
        self._squash(git, branch=branch, base=base, message=title)
        final_branch = branch
        if target_branch and target_branch != branch:
            for ref in (f"{SCRATCH_REF}/{branch}", f"{PUBLISHED_REF}/{branch}"):
                if self._reference_exists(git, ref):
                    git.run(
                        "update-ref",
                        ref[: -len(branch)] + target_branch,
                        ref,
                    )
                    git.run("update-ref", "-d", ref)
            git.run("branch", "-m", target_branch)
            final_branch = target_branch
        self.sync(
            workspace=workspace,
            upstream=upstream,
            base=base,
            branch=final_branch,
            token=token,
        )
        try:
            git.run(
                "push", self._fork_url(fork, token), f"{final_branch}:{final_branch}"
            )
        except GitError as error:
            raise _push_error(error) from error
        existing = self.client.find_pull(
            upstream=upstream, head=f"{login}:{final_branch}", base=base, token=token
        )
        if existing is not None:
            pull = existing
            created = False
        else:
            pull = self.client.create_pull(
                upstream=upstream,
                head=f"{login}:{final_branch}",
                base=base,
                title=title,
                body=body,
                token=token,
            )
            created = True
        git.run("update-ref", f"{PUBLISHED_REF}/{final_branch}", "HEAD")
        try:
            self.delete_remote_branch(
                repo=fork, branch=backup_branch(branch), token=token
            )
        except GitHubExportError:
            pass
        return PublishResult(
            pr_number=int(pull["number"]),
            url=pull.get("html_url", ""),
            created=created,
            branch=final_branch,
        )

    def open_pulls(
        self, *, upstream: str, head_repo: str, token: str
    ) -> list[PullRef]:
        pulls = self.client.list_pulls(upstream=upstream, state="open", token=token)
        heads: list[tuple[int, str, str]] = []
        for pull in pulls:
            head = pull.get("head") or {}
            if (head.get("repo") or {}).get("full_name") != head_repo:
                continue
            branch = head.get("ref") or ""
            if not branch:
                continue
            heads.append(
                (int(pull["number"]), branch, pull.get("title") or "")
            )

        def is_resumable(branch: str) -> bool:
            if branch.startswith(CHANGE_PREFIX):
                return True
            try:
                return self.client.branch_has_manifest(
                    repo=head_repo, branch=branch, token=token
                )
            except GitHubExportError:
                return True

        if heads:
            with ThreadPoolExecutor(max_workers=8) as pool:
                flags = list(pool.map(is_resumable, [branch for _, branch, _ in heads]))
        else:
            flags = []
        return [
            PullRef(number=number, branch=branch, title=title, resumable=resumable)
            for (number, branch, title), resumable in zip(heads, flags)
        ]

    def pr_status(self, *, upstream: str, number: int, token: str) -> PullState:
        pull = self.client.pull_state(upstream=upstream, number=number, token=token)
        reviews = self.client.pull_reviews(
            upstream=upstream, number=number, token=token
        )
        changes_requested = _changes_requested(reviews)
        merged = bool(pull.get("merged"))
        if merged:
            state = "merged"
        elif pull.get("state") == "closed":
            state = "closed"
        elif changes_requested:
            state = "changes_requested"
        else:
            state = "open"
        return PullState(
            state=state, merged=merged, changes_requested=changes_requested
        )

    def close_pull(self, *, upstream: str, number: int, token: str) -> None:
        self.client.close_pull(upstream=upstream, number=number, token=token)

    def delete_remote_branch(self, *, repo: str, branch: str, token: str) -> None:
        self.client.delete_branch(repo=repo, branch=branch, token=token)
