from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path
from typing import Any


class ExportService:
    def __init__(self, export_dir: Path) -> None:
        self.export_dir = export_dir
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export_json(self, entries: list[dict[str, Any]], name: str = "mynoh-export") -> Path:
        path = self.export_dir / f"{name}.json"
        path.write_text(json.dumps(entries, indent=2), encoding="utf-8")
        return path

    def export_csv(self, entries: list[dict[str, Any]], name: str = "mynoh-export") -> Path:
        path = self.export_dir / f"{name}.csv"
        keys = sorted({k for e in entries for k in e.keys()}) if entries else ["title"]
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader(); writer.writerows(entries)
        return path

    def export_markdown(self, entries: list[dict[str, Any]], name: str = "mynoh-export") -> Path:
        path = self.export_dir / f"{name}.md"
        lines = ["# Mynoh Knowledge Export", ""]
        for e in entries:
            lines += [f"## {e.get('title','Untitled')}", f"- Repository: {e.get('repository','')}", f"- Tags: {e.get('tags','')}", "", e.get("description", ""), ""]
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def export_html(self, entries: list[dict[str, Any]], name: str = "mynoh-export") -> Path:
        path = self.export_dir / f"{name}.html"
        cards = "".join(f"<article><h2>{e.get('title','')}</h2><p>{e.get('description','')}</p><code>{e.get('tags','')}</code></article>" for e in entries)
        path.write_text(f"<!doctype html><meta charset='utf-8'><title>Mynoh Export</title><body>{cards}</body>", encoding="utf-8")
        return path

    def export_zip(self, files: list[Path], name: str = "mynoh-export") -> Path:
        path = self.export_dir / f"{name}.zip"
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                if f.exists(): zf.write(f, arcname=f.name)
        return path
