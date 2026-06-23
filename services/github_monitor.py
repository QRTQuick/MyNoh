from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

from github.client import GitHubClient, GitHubCommit

log = logging.getLogger(__name__)
PromptCallback = Callable[[GitHubCommit], Awaitable[None]]


class GitHubPushMonitor:
    def __init__(self, client: GitHubClient, repo: str, branch: str, poll_seconds: int, prompt_delay_seconds: int) -> None:
        self.client = client
        self.repo = repo
        self.branch = branch
        self.poll_seconds = poll_seconds
        self.prompt_delay_seconds = prompt_delay_seconds
        self._last_sha = ""
        self._running = False

    async def run(self, on_push: PromptCallback) -> None:
        self._running = True
        while self._running:
            commit = self.client.latest_commit(self.repo, self.branch)
            if commit and self._last_sha and commit.sha != self._last_sha:
                log.info("Detected new push %s", commit.sha)
                await asyncio.sleep(self.prompt_delay_seconds)
                await on_push(commit)
            if commit:
                self._last_sha = commit.sha
            await asyncio.sleep(self.poll_seconds)

    def stop(self) -> None:
        self._running = False
