import uuid

from fastapi import APIRouter, Depends

from gamenet.server.db import get_connection, utc_now_iso
from gamenet.server.models.package import PackageCreateRequest, PackageResponse
from gamenet.server.security.auth import require_permission
from gamenet.server.services.audit_service import AuditService

router = APIRouter(prefix="/packages", tags=["packages"])


@router.get("", response_model=list[PackageResponse])
def list_packages(_user: dict = Depends(require_permission("packages.view"))) -> list[PackageResponse]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM packages WHERE active = 1 ORDER BY duration_seconds").fetchall()
    return [PackageResponse(**{**dict(row), "active": bool(row["active"])}) for row in rows]


@router.post("", response_model=PackageResponse, status_code=201)
def create_package(payload: PackageCreateRequest, user: dict = Depends(require_permission("packages.manage"))) -> PackageResponse:
    package_id = f"PACKAGE-{uuid.uuid4().hex[:12].upper()}"
    now = utc_now_iso()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO packages (id, name, duration_seconds, price, expiry_days, bonus_seconds, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (package_id, payload.name, payload.duration_seconds, payload.price, payload.expiry_days, payload.bonus_seconds, now, now),
        )
        AuditService.record(
            conn, action="PACKAGE_CREATED", entity_type="PACKAGE", entity_id=package_id,
            user_id=user["id"], new_value=payload.model_dump(),
        )
        row = conn.execute("SELECT * FROM packages WHERE id = ?", (package_id,)).fetchone()
    return PackageResponse(**{**dict(row), "active": bool(row["active"])})