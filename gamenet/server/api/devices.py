import sqlite3
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends

from gamenet.server.db import get_connection, utc_now_iso
from gamenet.server.models.heartbeat import HeartbeatRequest, HeartbeatResponse
from gamenet.server.security.device import authenticate_device, device_token

router = APIRouter(prefix="/devices", tags=["devices"])


def _heartbeat(conn: sqlite3.Connection, pc_id: str, payload: HeartbeatRequest, token: str | None) -> HeartbeatResponse:
    authenticate_device(conn, pc_id, token)
    now = datetime.now(UTC).replace(microsecond=0)
    now_iso = now.isoformat().replace("+00:00", "Z")
    pc = conn.execute("SELECT status FROM pcs WHERE id = ?", (pc_id,)).fetchone()
    if pc["status"] not in ("MAINTENANCE", "LOCKED"):
        conn.execute("UPDATE pcs SET status = ?, agent_version = ?, last_seen_at = ?, updated_at = ? WHERE id = ?", (payload.pc_state, payload.agent_version, now_iso, now_iso, pc_id))
    session = None
    if payload.session_id:
        session = conn.execute("SELECT id, status, lease_id, lease_expires_at FROM sessions WHERE id = ? AND pc_id = ?", (payload.session_id, pc_id)).fetchone()
        if session and session["status"] == "ACTIVE":
            lease_expires = (now + timedelta(seconds=10)).isoformat().replace("+00:00", "Z")
            conn.execute("UPDATE sessions SET lease_expires_at = ?, updated_at = ? WHERE id = ?", (lease_expires, now_iso, payload.session_id))
            session = conn.execute("SELECT id, status, lease_id, lease_expires_at FROM sessions WHERE id = ?", (payload.session_id,)).fetchone()
    conn.execute("INSERT INTO client_events (id, pc_id, event_type, agent_version, session_id, created_at) VALUES (?, ?, 'HEARTBEAT', ?, ?, ?)", (f"CLIENT-EVENT-{uuid.uuid4().hex[:12].upper()}", pc_id, payload.agent_version, payload.session_id, now_iso))
    return HeartbeatResponse(
        server_time=utc_now_iso(), pc_id=pc_id, pc_status=pc["status"] if pc["status"] in ("MAINTENANCE", "LOCKED") else payload.pc_state,
        session_id=session["id"] if session else None, session_status=session["status"] if session else None,
        lease_id=session["lease_id"] if session else None, lease_expires_at=session["lease_expires_at"] if session else None,
    )


@router.post("/{pc_id}/heartbeat", response_model=HeartbeatResponse)
def heartbeat(pc_id: str, payload: HeartbeatRequest, token: str | None = Depends(device_token)) -> HeartbeatResponse:
    with get_connection() as conn:
        return _heartbeat(conn, pc_id, payload, token)