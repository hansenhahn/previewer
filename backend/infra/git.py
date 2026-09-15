import os
import subprocess
from pathlib import Path


class GitError(RuntimeError):
    pass


def command(allow_file: bool = False) -> list[str]:
    return [
        "git",
        "-c",
        "credential.helper=",
        "-c",
        "protocol.file.allow=" + ("always" if allow_file else "never"),
        "-c",
        "user.name=previewer",
        "-c",
        "user.email=previewer@localhost",
    ]


def environment() -> dict:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_ASKPASS"] = "/bin/true"
    return env


class GitWorkspace:
    def __init__(
        self,
        path,
        *,
        allow_file: bool = False,
        timeout: int = 180,
        secrets: tuple[str, ...] = (),
    ):
        self.path = Path(path)
        self.allow_file = allow_file
        self.timeout = timeout
        self._secrets = tuple(secret for secret in secrets if secret)

    def _execute(self, args, cwd=None) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(
                command(self.allow_file) + list(args),
                cwd=str(cwd or self.path),
                env=environment(),
                capture_output=True,
                timeout=self.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise GitError("tempo esgotado na operação git") from exc

    def run(
        self,
        *args: str,
        cwd=None,
        capture: bool = False,
        check: bool = True,
    ) -> bytes:
        result = self._execute(args, cwd=cwd)
        if check and result.returncode != 0:
            raise GitError(
                self._sanitize(result.stderr.decode("utf-8", "replace").strip())
            )
        return result.stdout if capture else b""

    def returncode(self, *args: str, cwd=None) -> int:
        return self._execute(args, cwd=cwd).returncode

    def _sanitize(self, message: str) -> str:
        for secret in self._secrets:
            message = message.replace(secret, "***")
        return message or "falha na operação git"
