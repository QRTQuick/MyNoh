from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import requests

log = logging.getLogger(__name__)


@dataclass(slots=True)
class GitHubCommit:
    sha: str
    message: str
    pushed_at: str
    url: str


class GitHubClient:
    def __init__(self, username: str, token: str, timeout: int = 15) -> None:
        self.username = username
        self.token = token
        self.timeout = timeout
        self.base = "https://api.github.com"

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def latest_commit(self, repo: str, branch: str) -> GitHubCommit | None:
        owner_repo = repo if "/" in repo else f"{self.username}/{repo}"
        url = f"{self.base}/repos/{owner_repo}/commits/{branch}"
        try:
            resp = requests.get(url, headers=self._headers(), timeout=self.timeout)
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
            commit = data.get("commit", {})
            return GitHubCommit(
                sha=data.get("sha", ""),
                message=commit.get("message", ""),
                pushed_at=commit.get("committer", {}).get("date", ""),
                url=data.get("html_url", ""),
            )
        except Exception as exc:
            log.warning("GitHub latest commit failed: %s", exc)
            return None

    def validate(self) -> bool:
        try:
            resp = requests.get(f"{self.base}/user", headers=self._headers(), timeout=self.timeout)
            return resp.status_code in {200, 401} if not self.token else resp.ok
        except Exception:
            return False
