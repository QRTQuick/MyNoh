from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class GitRepositoryState:
    repository: str = ""
    branch: str = ""
    commit: str = ""
    remote_url: str = ""
    root: str = ""


class GitRepositoryDetector:
    def detect(self, cwd: Path | None = None) -> GitRepositoryState:
        cwd = cwd or Path.cwd()
        def git(*args: str) -> str:
            return subprocess.check_output(["git", *args], cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()
        try:
            root = git("rev-parse", "--show-toplevel")
            branch = git("branch", "--show-current")
            commit = git("rev-parse", "HEAD")
            remote = git("config", "--get", "remote.origin.url")
            name = Path(remote.removesuffix(".git")).name if remote else Path(root).name
            return GitRepositoryState(name, branch, commit, remote, root)
        except Exception:
            return GitRepositoryState()
