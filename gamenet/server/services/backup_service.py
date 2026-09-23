import sqlite3
from pathlib import Path


class BackupService:
    def __init__(self, source: sqlite3.Connection):
        self._source = source

    def backup(self, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            destination.unlink()
        target = sqlite3.connect(destination)
        try:
            self._source.backup(target)
            result = target.execute("PRAGMA integrity_check").fetchone()[0]
            if result != "ok":
                raise RuntimeError(f"Backup integrity check failed: {result}")
        finally:
            target.close()
        return destination

    @staticmethod
    def integrity_check(source: sqlite3.Connection) -> bool:
        return source.execute("PRAGMA integrity_check").fetchone()[0] == "ok"