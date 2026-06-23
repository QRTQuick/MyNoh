from pathlib import Path
from database.connection import Database
from database.repositories import IssueRepository
from models.entities import Issue

path = Path("assets/sample_mynoh.sqlite3")
db = Database(path); db.initialize()
repo = IssueRepository(db)
repo.add(Issue(title="JWT authentication bug", description="Refresh tokens failed after deployment.", root_cause="Clock skew and invalid issuer config.", programming_language="Python", framework="FastAPI", repository="api", branch="main", difficulty="Hard", tags="jwt,auth,fastapi"), solution="Normalized server time and fixed JWT issuer/audience settings.")
repo.add(Issue(title="React routing issue", description="Nested route rendered blank page.", root_cause="Outlet missing in parent layout.", programming_language="TypeScript", framework="React", repository="web", branch="main", difficulty="Medium", tags="react,routing"), solution="Added <Outlet /> and route tests.")
print(path)
