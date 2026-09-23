import uuid

from fastapi import APIRouter, Depends, HTTPException

from gamenet.server.db import get_connection, utc_now_iso
from gamenet.server.models.reservation import ReservationCreateRequest, ReservationResponse
from gamenet.server.security.auth import require_permission
from gamenet.server.services.audit_service import AuditService

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.post("", response_model=ReservationResponse, status_code=201)
def create_reservation(payload: ReservationCreateRequest, user: dict = Depends(require_permission("reservations.manage"))) -> ReservationResponse:
    reservation_id = f"RES-{uuid.uuid4().hex[:12].upper()}"
    with get_connection() as conn:
        existing = conn.execute("SELECT * FROM reservations WHERE request_id = ?", (payload.request_id,)).fetchone()
        if existing:
            return ReservationResponse(**dict(existing))
        customer = conn.execute("SELECT id FROM customers WHERE id = ? AND status = 'ACTIVE'", (payload.customer_id,)).fetchone()
        pc = conn.execute("SELECT id FROM pcs WHERE id = ? AND status != 'RETIRED'", (payload.pc_id,)).fetchone()
        if not customer or not pc:
            raise HTTPException(status_code=404, detail="Customer or PC not found")
        conflict = conn.execute(
            """
            SELECT id FROM reservations
            WHERE pc_id = ? AND status = 'ACTIVE' AND starts_at < ? AND ends_at > ?
            LIMIT 1
            """,
            (payload.pc_id, payload.ends_at, payload.starts_at),
        ).fetchone()
        if conflict:
            raise HTTPException(status_code=409, detail="Reservation conflicts with an existing reservation")
        conn.execute(
            "INSERT INTO reservations (id, customer_id, pc_id, starts_at, ends_at, request_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (reservation_id, payload.customer_id, payload.pc_id, payload.starts_at, payload.ends_at, payload.request_id, utc_now_iso()),
        )
        AuditService.record(conn, action="RESERVATION_CREATED", entity_type="RESERVATION", entity_id=reservation_id, user_id=user["id"], customer_id=payload.customer_id, pc_id=payload.pc_id, request_id=payload.request_id)
        return ReservationResponse(**dict(conn.execute("SELECT * FROM reservations WHERE id = ?", (reservation_id,)).fetchone()))