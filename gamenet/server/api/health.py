from fastapi import APIRouter

from gamenet import __version__
from gamenet.server.config import settings
from gamenet.server.db import get_connection, run_migrations
from gamenet.server.models.schemas import HealthResponse
from gamenet.server.services.recovery_service import RecoveryService

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    run_migrations()
    with get_connection() as conn:
        RecoveryService.pause_expired_leases(conn)
        conn.execute("SELECT 1").fetchone()
        database_integrity = RecoveryService.integrity_ok(conn)
        rows = conn.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        ).fetchall()
        applied = [row["version"] for row in rows]

    return HealthResponse(
        status="ok" if database_integrity else "degraded",
        version=__version__,
        database=str(settings.database_path),
        migrations_applied=applied,
        database_integrity=database_integrity,
    )
