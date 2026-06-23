from database.connection import Database
from database.repositories import IssueRepository
from models.entities import Issue


def test_issue_insert_and_search(tmp_path):
    db = Database(tmp_path / "test.sqlite3")
    db.initialize()
    repo = IssueRepository(db)
    issue_id = repo.add(Issue(title="SQL injection bug", description="Unsafe query", programming_language="Python", framework="FastAPI", repository="api", tags="security,sql"), solution="Used parameterized queries")
    assert issue_id > 0
    rows = repo.search("SQL")
    assert rows and rows[0]["title"] == "SQL injection bug"
    filtered = repo.search("", {"language": "Python", "tag": "security"})
    assert len(filtered) == 1
