# API Documentation

## KnowledgeService

- `capture_bug(payload: dict) -> int`
- `search(query: str, filters: dict | None) -> list[dict]`
- `timeline(limit: int) -> list[dict]`

## SearchService

- `natural_language_search(prompt: str) -> list[dict]`

## GitHubClient

- `latest_commit(repo: str, branch: str) -> GitHubCommit | None`
- `validate() -> bool`
