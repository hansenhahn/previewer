from concurrent.futures import ThreadPoolExecutor

from infra.github_source import check_manifest


def refresh_repositories(
    *, store, provider, user_id, token, checker=None, workers: int = 8
):
    if checker is None:
        checker = check_manifest
    repos = provider.list_repos(token)
    store.refresh(user_id, provider.name, repos)
    rows = store.list_for_user(user_id, provider.name)
    checks: dict[str, tuple[bool, str | None]] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pending = {
            pool.submit(
                checker, row.full_name, row.default_branch, token=token
            ): row.full_name
            for row in rows
        }
        for future, full_name in pending.items():
            try:
                checks[full_name] = future.result()
            except Exception:
                checks[full_name] = (False, "falha ao verificar o manifest")
    store.record_checks(user_id, provider.name, checks)
    return store.list_for_user(user_id, provider.name)
