from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException

from gamenet.server.db import get_connection, utc_now_iso
from gamenet.server.models.customer_auth import CustomerLoginRequest, CustomerLoginResponse
from gamenet.server.security.device import authenticate_device, device_token
from gamenet.server.security.passwords import verify_secret

router = APIRouter(prefix="/devices", tags=["customer-auth"])


@router.post("/{pc_id}/customer-login", response_model=CustomerLoginResponse)
def customer_login(
    pc_id: str,
    payload: CustomerLoginRequest,
    token: str | None = Depends(device_token),
) -> CustomerLoginResponse:
    with get_connection() as conn:
        authenticate_device(conn, pc_id, token)
        row = conn.execute(
            """
            SELECT c.*, a.pin_hash, a.failed_attempts, a.locked_until
            FROM customers c JOIN customer_auth a ON a.customer_id = c.id
            WHERE c.customer_number = ? AND c.status = 'ACTIVE'
            """,
            (payload.customer_number,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Invalid customer credentials")
        if row["locked_until"] and row["locked_until"] > utc_now_iso():
            raise HTTPException(status_code=423, detail="Customer login temporarily locked")
        if not verify_secret(payload.pin, row["pin_hash"]):
            failed_attempts = row["failed_attempts"] + 1
            locked_until = None
            if failed_attempts >= 5:
                locked_until = (datetime.now(UTC) + timedelta(minutes=5)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            conn.execute(
                "UPDATE customer_auth SET failed_attempts = ?, locked_until = ?, updated_at = ? WHERE customer_id = ?",
                (failed_attempts, locked_until, utc_now_iso(), row["id"]),
            )
            conn.commit()
            raise HTTPException(status_code=401, detail="Invalid customer credentials")
        conn.execute(
            "UPDATE customer_auth SET failed_attempts = 0, locked_until = NULL, updated_at = ? WHERE customer_id = ?",
            (utc_now_iso(), row["id"]),
        )
        credit = conn.execute(
            """
            SELECT COALESCE(SUM(granted_seconds - consumed_seconds), 0) AS total
            FROM entitlements WHERE customer_id = ? AND status = 'ACTIVE'
              AND (expires_at IS NULL OR expires_at > ?)
            """,
            (row["id"], utc_now_iso()),
        ).fetchone()
        session = conn.execute(
            """
            SELECT id, status FROM sessions
            WHERE customer_id = ? AND status IN ('CREATED', 'ACTIVE', 'PAUSED', 'CONNECTION_LOST')
            ORDER BY created_at DESC LIMIT 1
            """,
            (row["id"],),
        ).fetchone()
        return CustomerLoginResponse(
            customer_id=row["id"], customer_number=row["customer_number"], name=row["name"],
            gaming_credit_seconds=int(credit["total"]),
            active_session_id=session["id"] if session else None,
            active_session_status=session["status"] if session else None,
        )