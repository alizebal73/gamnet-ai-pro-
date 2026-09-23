import uuid

from fastapi import APIRouter, Depends

from gamenet.server.db import get_connection, utc_now_iso
from gamenet.server.models.vip import VipPlanCreateRequest, VipPlanResponse
from gamenet.server.security.auth import require_permission
from gamenet.server.services.audit_service import AuditService

router = APIRouter(prefix="/vip", tags=["vip"])


@router.get("/plans", response_model=list[VipPlanResponse])
def list_vip_plans(_user: dict = Depends(require_permission("vip.view"))) -> list[VipPlanResponse]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM vip_plans WHERE active = 1 ORDER BY duration_days").fetchall()
    return [VipPlanResponse(**{**dict(row), "active": bool(row["active"])}) for row in rows]


@router.post("/plans", response_model=VipPlanResponse, status_code=201)
def create_vip_plan(payload: VipPlanCreateRequest, user: dict = Depends(require_permission("vip.manage"))) -> VipPlanResponse:
    plan_id = f"VIP-{uuid.uuid4().hex[:12].upper()}"
    now = utc_now_iso()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO vip_plans (id, name, duration_days, price, discount_percent, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (plan_id, payload.name, payload.duration_days, payload.price, payload.discount_percent, now, now),
        )
        AuditService.record(conn, action="VIP_PLAN_CREATED", entity_type="VIP_PLAN", entity_id=plan_id, user_id=user["id"], new_value=payload.model_dump())
        row = conn.execute("SELECT * FROM vip_plans WHERE id = ?", (plan_id,)).fetchone()
    return VipPlanResponse(**{**dict(row), "active": bool(row["active"])})