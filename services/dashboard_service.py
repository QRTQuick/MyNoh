from __future__ import annotations

from collections import Counter
from typing import Any

from database.connection import Database


class DashboardService:
    def __init__(self, db: Database) -> None:
        self.db = db

    def stats(self) -> dict[str, Any]:
        with self.db.session() as conn:
            total = conn.execute("SELECT COUNT(*) c FROM issues").fetchone()["c"]
            repos = conn.execute("SELECT COUNT(DISTINCT repository) c FROM issues WHERE repository!=''").fetchone()["c"]
            minutes = conn.execute("SELECT COALESCE(SUM(time_spent_minutes),0) m FROM issues").fetchone()["m"]
            rows = [dict(r) for r in conn.execute("SELECT programming_language, framework, created_at FROM issues")]
        langs = Counter(r["programming_language"] for r in rows if r["programming_language"]).most_common(8)
        frameworks = Counter(r["framework"] for r in rows if r["framework"]).most_common(8)
        return {
            "total_bugs_solved": total,
            "knowledge_entries": total,
            "hours_saved": round((minutes or 0) / 60 * 1.5, 1),
            "repositories_tracked": repos,
            "languages": langs,
            "frameworks": frameworks,
        }
