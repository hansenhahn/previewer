from infra.project_export import PublishResult, PullRef, PullState


class FakeProjectExport:
    def __init__(self, *, upstream="upstream/projeto", base="main", head="alice/projeto"):
        self.calls = []
        self.upstream = upstream
        self.head = head
        self.base = base
        self.pulls: list[PullRef] = []
        self.branch = None
        self.pending = False
        self.pr_number = None
        self.pr_state = "open"
        self.pr_url = "https://github.com/alice/projeto/pull/12"

    def origin_remote(self, *, workspace):
        return self.head

    def default_branch(self, *, workspace):
        return self.base

    def checkout_base(self, *, workspace, base):
        self.branch = None
        self.calls.append(("checkout_base", base))

    def backup(self, *, workspace, repo, branch, token):
        self.calls.append(("backup", repo, branch))

    def current_branch(self, *, workspace):
        return self.branch or self.base

    def branch_exists(self, *, workspace, branch):
        return branch == self.branch

    def ensure_branch(self, *, workspace, branch, base):
        self.branch = branch
        self.calls.append(("ensure_branch", branch))

    def commit(self, *, workspace, branch, base, message):
        self.calls.append(("commit", message))

    def has_uncommitted(self, *, workspace):
        return self.pending

    def has_unpushed(self, *, workspace, branch, base):
        return self.pending

    def restore(self, *, workspace, branch, base):
        self.pending = False
        self.calls.append(("restore", branch))

    def resume(self, *, workspace, branch, base):
        self.branch = branch
        self.calls.append(("resume", branch))

    def abandon(self, *, workspace, branch, base):
        self.branch = None
        self.calls.append(("abandon", branch))

    def ensure_fork(self, *, upstream, login, token, base):
        self.fork = f"{login}/{upstream.split('/')[-1]}"
        self.calls.append(("ensure_fork", self.fork))
        return self.fork

    def sync(self, *, workspace, upstream, base, branch, token):
        return True

    def publish(
        self,
        *,
        workspace,
        upstream,
        base,
        branch,
        login,
        token,
        title,
        body,
        target_branch=None,
    ):
        self.published = True
        self.pr_number = 12
        self.branch = target_branch or branch
        self.calls.append(("publish", title))
        return PublishResult(
            pr_number=12, url=self.pr_url, created=True, branch=self.branch
        )

    def open_pulls(self, *, upstream, head_repo, token):
        self.calls.append(("open_pulls", head_repo))
        return list(self.pulls)

    def pr_status(self, *, upstream, number, token):
        return PullState(
            state=self.pr_state,
            merged=self.pr_state == "merged",
            changes_requested=self.pr_state == "changes_requested",
        )

    def close_pull(self, *, upstream, number, token):
        self.calls.append(("close_pull", number))

    def delete_remote_branch(self, *, repo, branch, token):
        self.calls.append(("delete_remote_branch", branch))
