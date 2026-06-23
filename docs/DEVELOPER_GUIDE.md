# Developer Guide

Mynoh follows Clean Architecture. UI depends on services; services depend on repository protocols; repositories encapsulate SQLite. To migrate to PostgreSQL/MySQL, implement repositories with the same protocols and inject them into services.

Run tests:

```bash
pytest -q
```
