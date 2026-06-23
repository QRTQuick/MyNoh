from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Iterable, Protocol

from database.connection import Database
from models.entities import CodeSnippet, Issue, Link, Note, Repository, Solution, utc_now


class IssueRepositoryProtocol(Protocol):
    def add(self, issue: Issue, solution: str = "", snippets: Iterable[CodeSnippet] = ()) -> int: ...
    def search(self, query: str = "", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]: ...
    def list_recent(self, limit: int = 50) -> list[dict[str, Any]]: ...


class IssueRepository(IssueRepositoryProtocol):
    def __init__(self, db: Database) -> None:
        self.db = db

    def add(self, issue: Issue, solution: str = "", snippets: Iterable[CodeSnippet] = ()) -> int:
        data = asdict(issue)
        data.pop("id", None)
        cols = ", ".join(data.keys())
        placeholders = ", ".join([":" + k for k in data])
        with self.db.session() as conn:
            cur = conn.execute(f"INSERT INTO issues ({cols}) VALUES ({placeholders})", data)
            issue_id = int(cur.lastrowid)
            if solution:
                conn.execute(
                    "INSERT INTO solutions (issue_id, content, created_at) VALUES (?, ?, ?)",
                    (issue_id, solution, utc_now()),
                )
            for snip in snippets:
                conn.execute(
                    "INSERT INTO code_snippets (issue_id, language, title, code, created_at) VALUES (?, ?, ?, ?, ?)",
                    (issue_id, snip.language, snip.title, snip.code, utc_now()),
                )
            for tag in [t.strip() for t in issue.tags.split(",") if t.strip()]:
                conn.execute("INSERT OR IGNORE INTO tags(name) VALUES (?)", (tag,))
                tag_id = conn.execute("SELECT id FROM tags WHERE name=?", (tag,)).fetchone()["id"]
                conn.execute("INSERT OR IGNORE INTO issue_tags(issue_id, tag_id) VALUES (?, ?)", (issue_id, tag_id))
            return issue_id

    def update(self, issue_id: int, fields: dict[str, Any]) -> None:
        allowed = {"title","description","root_cause","difficulty","programming_language","framework","repository","branch","commit_hash","files_affected","stack_overflow_used","ai_assistant_used","time_spent_minutes","tags"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return
        updates["updated_at"] = utc_now()
        set_clause = ", ".join(f"{k}=:{k}" for k in updates)
        updates["id"] = issue_id
        with self.db.session() as conn:
            conn.execute(f"UPDATE issues SET {set_clause} WHERE id=:id", updates)

    def search(self, query: str = "", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        filters = filters or {}
        params: list[Any] = []
        where: list[str] = []
        base = "SELECT i.* FROM issues i"
        if query.strip():
            base += " JOIN issues_fts f ON i.id = f.rowid"
            where.append("issues_fts MATCH ?")
            params.append(query)
        mapping = {
            "language": "i.programming_language",
            "framework": "i.framework",
            "repository": "i.repository",
            "difficulty": "i.difficulty",
            "tag": "i.tags",
            "file": "i.files_affected",
        }
        for key, col in mapping.items():
            val = filters.get(key)
            if val:
                where.append(f"{col} LIKE ?")
                params.append(f"%{val}%")
        if filters.get("date_from"):
            where.append("i.created_at >= ?")
            params.append(filters["date_from"])
        if filters.get("date_to"):
            where.append("i.created_at <= ?")
            params.append(filters["date_to"])
        sql = base + (" WHERE " + " AND ".join(where) if where else "") + " ORDER BY i.created_at DESC LIMIT 200"
        with self.db.session() as conn:
            return [dict(r) for r in conn.execute(sql, params).fetchall()]

    def list_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.db.session() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM issues ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()]

    def get_detail(self, issue_id: int) -> dict[str, Any] | None:
        with self.db.session() as conn:
            issue = conn.execute("SELECT * FROM issues WHERE id=?", (issue_id,)).fetchone()
            if not issue:
                return None
            result = dict(issue)
            result["solutions"] = [dict(r) for r in conn.execute("SELECT * FROM solutions WHERE issue_id=?", (issue_id,))]
            result["snippets"] = [dict(r) for r in conn.execute("SELECT * FROM code_snippets WHERE issue_id=?", (issue_id,))]
            result["links"] = [dict(r) for r in conn.execute("SELECT * FROM links WHERE issue_id=?", (issue_id,))]
            result["screenshots"] = [dict(r) for r in conn.execute("SELECT * FROM screenshots WHERE issue_id=?", (issue_id,))]
            return result


class RepositoryRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def upsert(self, repo: Repository) -> int:
        with self.db.session() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO repositories(name, remote_url, default_branch, provider, created_at) VALUES (?, ?, ?, ?, ?)",
                (repo.name, repo.remote_url, repo.default_branch, repo.provider, repo.created_at),
            )
            row = conn.execute("SELECT id FROM repositories WHERE name=? AND remote_url=?", (repo.name, repo.remote_url)).fetchone()
            return int(row["id"])


class SettingsRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def set(self, key: str, value: str, encrypted: bool = False) -> None:
        with self.db.session() as conn:
            conn.execute(
                "INSERT INTO settings(key, value, encrypted, updated_at) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value, encrypted=excluded.encrypted, updated_at=excluded.updated_at",
                (key, value, int(encrypted), utc_now()),
            )

    def get(self, key: str, default: str = "") -> str:
        with self.db.session() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
            return str(row["value"]) if row else default

    def all(self) -> dict[str, str]:
        with self.db.session() as conn:
            return {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM settings")}


class ActivityRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def log(self, event_type: str, details: dict[str, Any] | str = "") -> None:
        payload = details if isinstance(details, str) else json.dumps(details)
        with self.db.session() as conn:
            conn.execute("INSERT INTO activity_logs(event_type, details, created_at) VALUES (?, ?, ?)", (event_type, payload, utc_now()))
