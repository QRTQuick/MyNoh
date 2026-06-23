from __future__ import annotations

import json
import os
import platform
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

APP_NAME = "Mynoh"


def user_data_dir() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif platform.system() == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    elif os.environ.get("XDG_CONFIG_HOME"):
        base = Path(os.environ["XDG_CONFIG_HOME"])
    else:
        base = Path.home() / ".config"
    return base / APP_NAME.lower()


@dataclass(slots=True)
class AppConfig:
    data_dir: Path = field(default_factory=user_data_dir)
    database_path: Path | None = None
    export_dir: Path | None = None
    backup_dir: Path | None = None
    log_file: Path | None = None
    theme: str = "dark"
    reminder_interval_seconds: int = 360
    github_poll_seconds: int = 30
    post_push_prompt_delay_seconds: int = 30
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "07:00"

    def __post_init__(self) -> None:
        self.data_dir = Path(self.data_dir)
        self.database_path = Path(self.database_path or self.data_dir / "mynoh.sqlite3")
        self.export_dir = Path(self.export_dir or self.data_dir / "exports")
        self.backup_dir = Path(self.backup_dir or self.data_dir / "backups")
        self.log_file = Path(self.log_file or self.data_dir / "mynoh.log")
        for p in [self.data_dir, self.export_dir, self.backup_dir]:
            p.mkdir(parents=True, exist_ok=True)

    @classmethod
    def load(cls, path: Path | None = None) -> "AppConfig":
        path = path or user_data_dir() / "config.json"
        if not path.exists():
            cfg = cls()
            cfg.save(path)
            return cfg
        raw = json.loads(path.read_text(encoding="utf-8"))
        for key in ["data_dir", "database_path", "export_dir", "backup_dir", "log_file"]:
            if raw.get(key):
                raw[key] = Path(raw[key])
        return cls(**raw)

    def save(self, path: Path | None = None) -> None:
        path = path or self.data_dir / "config.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        data: dict[str, Any] = asdict(self)
        for key, value in data.items():
            if isinstance(value, Path):
                data[key] = str(value)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
