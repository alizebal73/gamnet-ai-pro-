from pathlib import Path

from gamenet.server.db import get_connection
from gamenet.server.services.backup_service import BackupService


def test_sqlite_backup_uses_backup_api_and_integrity_check(tmp_path: Path):
    destination = tmp_path / "backup" / "gamenet.db"
    with get_connection() as conn:
        assert BackupService.integrity_check(conn) is True
        result = BackupService(conn).backup(destination)

    assert result == destination
    assert destination.exists()