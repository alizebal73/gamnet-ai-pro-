from fastapi import APIRouter

from gamenet import __version__
from gamenet.server.config import settings
from gamenet.server.db import get_connection, run_migrations
from gamenet.server.models.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    run_migrations()
    with get_connection() as conn:
        conn.execute("SELECT 1").fetchone()
        rows = conn.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        ).fetchall()
        applied = [row["version"] for row in rows]

    return HealthResponse(
        status="ok",
        version=__version__,
        database=str(settings.database_path),
        migrations_applied=applied,
    )
