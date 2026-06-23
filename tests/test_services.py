from database.connection import Database
from database.repositories import IssueRepository
from services.knowledge_service import KnowledgeService
from services.search_service import SearchService


def test_capture_and_natural_language_search(tmp_path):
    db = Database(tmp_path / "test.sqlite3"); db.initialize()
    service = KnowledgeService(IssueRepository(db))
    service.capture_bug({"title":"React routing issue", "description":"blank page", "solution":"added Outlet", "programming_language":"TypeScript", "framework":"React", "tags":"react,routing"})
    search = SearchService(service)
    rows = search.natural_language_search("Find the React routing issue")
    assert rows[0]["framework"] == "React"
