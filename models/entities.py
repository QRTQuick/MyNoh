from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Difficulty(StrEnum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


@dataclass(slots=True)
class User:
    id: Optional[int] = None
    github_username: str = ""
    display_name: str = ""
    created_at: str = field(default_factory=utc_now)


@dataclass(slots=True)
class Repository:
    id: Optional[int] = None
    name: str = ""
    remote_url: str = ""
    default_branch: str = "main"
    provider: str = "github"
    created_at: str = field(default_factory=utc_now)


@dataclass(slots=True)
class Commit:
    id: Optional[int] = None
    repository_id: int = 0
    sha: str = ""
    branch: str = ""
    message: str = ""
    pushed_at: str = field(default_factory=utc_now)
    processed: bool = False


@dataclass(slots=True)
class Issue:
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    root_cause: str = ""
    difficulty: str = Difficulty.MEDIUM.value
    programming_language: str = ""
    framework: str = ""
    repository: str = ""
    branch: str = ""
    commit_hash: str = ""
    files_affected: str = ""
    stack_overflow_used: bool = False
    ai_assistant_used: bool = False
    time_spent_minutes: int = 0
    tags: str = ""
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)


@dataclass(slots=True)
class Solution:
    id: Optional[int] = None
    issue_id: int = 0
    content: str = ""
    created_at: str = field(default_factory=utc_now)


@dataclass(slots=True)
class Note:
    id: Optional[int] = None
    issue_id: Optional[int] = None
    title: str = ""
    markdown: str = ""
    created_at: str = field(default_factory=utc_now)


@dataclass(slots=True)
class CodeSnippet:
    id: Optional[int] = None
    issue_id: Optional[int] = None
    language: str = ""
    title: str = ""
    code: str = ""
    created_at: str = field(default_factory=utc_now)


@dataclass(slots=True)
class Link:
    id: Optional[int] = None
    issue_id: Optional[int] = None
    url: str = ""
    title: str = ""
    created_at: str = field(default_factory=utc_now)


@dataclass(slots=True)
class Screenshot:
    id: Optional[int] = None
    issue_id: Optional[int] = None
    file_path: str = ""
    caption: str = ""
    created_at: str = field(default_factory=utc_now)
