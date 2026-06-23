from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


class BackupService:
    def __init__(self, database_path: Path, backup_dir: Path) -> None:
        self.database_path = database_path
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, kind: str = "manual") -> Path:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        dest = self.backup_dir / f"mynoh-{kind}-{stamp}.sqlite3"
        shutil.copy2(self.database_path, dest)
        return dest

    def restore(self, backup_file: Path) -> None:
        if not backup_file.exists():
            raise FileNotFoundError(backup_file)
        shutil.copy2(backup_file, self.database_path)
