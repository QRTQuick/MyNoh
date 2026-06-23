from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from services.knowledge_service import KnowledgeService


class SearchService:
    """Hybrid keyword search now; semantic embedding provider can be injected later."""

    def __init__(self, knowledge: KnowledgeService) -> None:
        self.knowledge = knowledge

    def natural_language_search(self, prompt: str) -> list[dict[str, Any]]:
        filters: dict[str, Any] = {}
        text = prompt.lower()
        for lang in ["python", "java", "kotlin", "c#", "javascript", "typescript", "go", "rust", "c++", "sql", "json", "yaml"]:
            if re.search(rf"\b{re.escape(lang)}\b", text):
                filters["language"] = lang
        for difficulty in ["easy", "medium", "hard"]:
            if difficulty in text:
                filters["difficulty"] = difficulty.title()
        if "last year" in text:
            year = datetime.now(timezone.utc).year - 1
            filters["date_from"] = f"{year}-01-01"
            filters["date_to"] = f"{year}-12-31T23:59:59"
        keywords = re.sub(r"\b(show|find|search|every|the|i|solved|last year|bug|issue)\b", " ", prompt, flags=re.I)
        keywords = " ".join(keywords.split())
        return self.knowledge.search(keywords or prompt, filters)
