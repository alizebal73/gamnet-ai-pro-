import uuid

from fastapi import APIRouter, Depends, HTTPException

from gamenet.server.db import get_connection, utc_now_iso
from gamenet.server.models.shift import ShiftCloseRequest, ShiftOpenRequest, ShiftResponse
from gamenet.server.security.auth import require_permission
from gamenet.server.services.audit_service import AuditService

router = APIRouter(prefix="/shifts", tags=["shifts"])


def _response(row) -> ShiftResponse:
    return ShiftResponse(
        id=row["id"], user_id=row["user_id"], status=row["status"], opening_cash=row["opening_cash"],
        expected_cash=row["expected_cash"], actual_cash=row["actual_cash"], difference=row["difference"],
    )


@router.post("", response_model=ShiftResponse, status_code=201)
def open_shift(payload: ShiftOpenRequest, user: dict = Depends(require_permission("shifts.manage"))) -> ShiftResponse:
    now = utc_now_iso()
    shift_id = f"SHIFT-{uuid.uuid4().hex[:12].upper()}"
    with get_connection() as conn:
        existing = conn.execute("SELECT * FROM shifts WHERE user_id = ? AND status = 'OPEN'", (user["id"],)).fetchone()
        if existing:
            return _response(existing)
        conn.execute(
            "INSERT INTO shifts (id, user_id, opening_cash, expected_cash, opened_at) VALUES (?, ?, ?, ?, ?)",
            (shift_id, user["id"], payload.opening_cash, payload.opening_cash, now),
        )
        AuditService.record(conn, action="SHIFT_OPENED", entity_type="SHIFT", entity_id=shift_id, user_id=user["id"], request_id=payload.request_id, amount=payload.opening_cash)
        return _response(conn.execute("SELECT * FROM shifts WHERE id = ?", (shift_id,)).fetchone())


@router.post("/{shift_id}/close", response_model=ShiftResponse)
def close_shift(shift_id: str, payload: ShiftCloseRequest, user: dict = Depends(require_permission("shifts.manage"))) -> ShiftResponse:
    now = utc_now_iso()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM shifts WHERE id = ? AND user_id = ?", (shift_id, user["id"])).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Shift not found")
        if row["status"] == "CLOSED":
            return _response(row)
        movement_total = conn.execute("SELECT COALESCE(SUM(delta_amount), 0) AS total FROM cash_movements WHERE shift_id = ?", (shift_id,)).fetchone()["total"]
        expected = row["opening_cash"] + movement_total
        difference = payload.actual_cash - expected
        conn.execute("UPDATE shifts SET status = 'CLOSED', expected_cash = ?, actual_cash = ?, difference = ?, closed_at = ?, close_reason = ? WHERE id = ?", (expected, payload.actual_cash, difference, now, payload.reason, shift_id))
        AuditService.record(conn, action="SHIFT_CLOSED", entity_type="SHIFT", entity_id=shift_id, user_id=user["id"], request_id=payload.request_id, amount=difference, reason=payload.reason, new_value={"expected_cash": expected, "actual_cash": payload.actual_cash})
        return _response(conn.execute("SELECT * FROM shifts WHERE id = ?", (shift_id,)).fetchone())