from __future__ import annotations

from typing import Any

from database.repositories import IssueRepositoryProtocol
from models.entities import CodeSnippet, Issue


class KnowledgeService:
    def __init__(self, issues: IssueRepositoryProtocol) -> None:
        self.issues = issues

    def capture_bug(self, payload: dict[str, Any]) -> int:
        title = str(payload.get("title") or payload.get("problem") or "Untitled issue").strip()
        if not title:
            raise ValueError("Problem title is required")
        issue = Issue(
            title=title,
            description=str(payload.get("description", "")),
            root_cause=str(payload.get("root_cause", "")),
            difficulty=str(payload.get("difficulty", "Medium")),
            programming_language=str(payload.get("programming_language", payload.get("technology", ""))),
            framework=str(payload.get("framework", "")),
            repository=str(payload.get("repository", "")),
            branch=str(payload.get("branch", "")),
            commit_hash=str(payload.get("commit_hash", "")),
            files_affected=str(payload.get("files_affected", "")),
            stack_overflow_used=bool(payload.get("stack_overflow_used", False)),
            ai_assistant_used=bool(payload.get("ai_assistant_used", False)),
            time_spent_minutes=int(payload.get("time_spent_minutes", payload.get("time_spent", 0)) or 0),
            tags=str(payload.get("tags", payload.get("keywords", ""))),
        )
        snippets = []
        if payload.get("code_snippet"):
            snippets.append(CodeSnippet(language=issue.programming_language, title=title, code=str(payload["code_snippet"])))
        return self.issues.add(issue, solution=str(payload.get("solution", payload.get("solved", ""))), snippets=snippets)

    def search(self, query: str, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return self.issues.search(query, filters)

    def timeline(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.issues.list_recent(limit)
