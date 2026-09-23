import sqlite3
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException

from gamenet.server.db import utc_now_iso
from gamenet.server.models.session import SessionActionRequest, SessionConsumeRequest, SessionResponse, SessionStartRequest
from gamenet.server.services.audit_service import AuditService
from gamenet.server.services.idempotency import claim_request


class SessionService:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    @staticmethod
    def _response(row: sqlite3.Row) -> SessionResponse:
        return SessionResponse(
            id=row["id"], customer_id=row["customer_id"], pc_id=row["pc_id"],
            status=row["status"], consumed_seconds=row["consumed_seconds"],
            lease_id=row["lease_id"], lease_expires_at=row["lease_expires_at"],
        )

    def start(self, payload: SessionStartRequest, user_id: str) -> SessionResponse:
        existing = self._conn.execute(
            "SELECT * FROM sessions WHERE request_id = ?", (payload.request_id,)
        ).fetchone()
        if existing:
            return self._response(existing)

        customer = self._conn.execute("SELECT id FROM customers WHERE id = ? AND status = 'ACTIVE'", (payload.customer_id,)).fetchone()
        pc = self._conn.execute("SELECT id, status FROM pcs WHERE id = ?", (payload.pc_id,)).fetchone()
        if not customer or not pc:
            raise HTTPException(status_code=404, detail="Customer or PC not found")
        if pc["status"] not in ("ONLINE", "READY"):
            raise HTTPException(status_code=409, detail="PC is not available")
        balance = self._conn.execute(
            """
            SELECT COALESCE(SUM(granted_seconds - consumed_seconds), 0) AS total
            FROM entitlements WHERE customer_id = ? AND status = 'ACTIVE'
              AND (expires_at IS NULL OR expires_at > ?)
            """, (payload.customer_id, utc_now_iso())
        ).fetchone()["total"]
        if balance <= 0:
            raise HTTPException(status_code=409, detail="Customer has no valid credit")

        now = datetime.now(UTC).replace(microsecond=0)
        now_iso = now.isoformat().replace("+00:00", "Z")
        session_id = f"SESSION-{uuid.uuid4().hex[:12].upper()}"
        lease_id = f"LEASE-{uuid.uuid4().hex[:12].upper()}"
        lease_expires = (now + timedelta(seconds=10)).isoformat().replace("+00:00", "Z")
        try:
            self._conn.execute(
                """
                INSERT INTO sessions
                    (id, customer_id, pc_id, status, lease_id, lease_expires_at, started_at, created_at, updated_at, request_id)
                VALUES (?, ?, ?, 'ACTIVE', ?, ?, ?, ?, ?, ?)
                """,
                (session_id, payload.customer_id, payload.pc_id, lease_id, lease_expires,
                 now_iso, now_iso, now_iso, payload.request_id),
            )
        except sqlite3.IntegrityError as error:
            if "idx_one_active" in str(error):
                raise HTTPException(status_code=409, detail="Customer or PC already has an active session") from error
            raise
        self._conn.execute(
            "UPDATE pcs SET status = 'BUSY', updated_at = ? WHERE id = ?", (now_iso, payload.pc_id)
        )
        self._event(session_id, "STARTED", None, user_id, now_iso)
        AuditService.record(
            self._conn, action="SESSION_STARTED", entity_type="SESSION", entity_id=session_id,
            request_id=payload.request_id, user_id=user_id, customer_id=payload.customer_id,
            pc_id=payload.pc_id, new_value={"status": "ACTIVE"},
        )
        return self._response(self._conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone())

    def action(self, session_id: str, payload: SessionActionRequest, user_id: str, action: str) -> SessionResponse:
        row = self._conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Session not found")
        if not claim_request(
            self._conn, request_id=payload.request_id, operation=f"SESSION_{action.upper()}",
            entity_type="SESSION", entity_id=session_id,
        ):
            return self._response(row)
        transitions = {"pause": ("ACTIVE", "PAUSED", "PAUSED"), "resume": ("PAUSED", "ACTIVE", "RESUMED"), "end": (("ACTIVE", "PAUSED"), "ENDED", "ENDED")}
        allowed, target, event = transitions[action]
        if row["status"] not in ((allowed,) if isinstance(allowed, str) else allowed):
            raise HTTPException(status_code=409, detail=f"Cannot {action} session in current state")
        now = utc_now_iso()
        self._conn.execute(
            "UPDATE sessions SET status = ?, paused_at = CASE WHEN ? = 'PAUSED' THEN ? ELSE paused_at END, ended_at = CASE WHEN ? = 'ENDED' THEN ? ELSE ended_at END, updated_at = ? WHERE id = ?",
            (target, target, now, target, now, now, session_id),
        )
        if target == "ENDED":
            self._conn.execute("UPDATE pcs SET status = 'READY', updated_at = ? WHERE id = ?", (now, row["pc_id"]))
        self._event(session_id, event, payload.reason, user_id, now)
        AuditService.record(
            self._conn, action=f"SESSION_{event}", entity_type="SESSION", entity_id=session_id,
            request_id=payload.request_id, user_id=user_id, customer_id=row["customer_id"],
            pc_id=row["pc_id"], reason=payload.reason,
            old_value={"status": row["status"]}, new_value={"status": target},
        )
        return self._response(self._conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone())

    def consume(self, session_id: str, payload: SessionConsumeRequest) -> SessionResponse:
        duplicate = self._conn.execute("SELECT session_id FROM session_consumptions WHERE request_id = ?", (payload.request_id,)).fetchone()
        if duplicate:
            return self._response(self._conn.execute("SELECT * FROM sessions WHERE id = ?", (duplicate["session_id"],)).fetchone())
        session = self._conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not session or session["status"] != "ACTIVE":
            raise HTTPException(status_code=409, detail="Session is not active")
        if not claim_request(
            self._conn, request_id=payload.request_id, operation="SESSION_CONSUME",
            entity_type="SESSION", entity_id=session_id,
        ):
            return self._response(session)
        remaining = payload.seconds
        now = utc_now_iso()
        entitlements = self._conn.execute(
            """
            SELECT * FROM entitlements
            WHERE customer_id = ? AND status = 'ACTIVE' AND consumed_seconds < granted_seconds
              AND (expires_at IS NULL OR expires_at > ?)
            ORDER BY expires_at IS NULL, expires_at, created_at
            """, (session["customer_id"], now)
        ).fetchall()
        for entitlement in entitlements:
            available = entitlement["granted_seconds"] - entitlement["consumed_seconds"]
            consumed = min(available, remaining)
            self._conn.execute("UPDATE entitlements SET consumed_seconds = consumed_seconds + ?, updated_at = ? WHERE id = ?", (consumed, now, entitlement["id"]))
            ledger_request_id = f"{payload.request_id}:{entitlement['id']}"
            self._conn.execute("INSERT INTO entitlement_ledger (id, entitlement_id, customer_id, delta_seconds, event_type, request_id, created_at) VALUES (?, ?, ?, ?, 'CONSUMPTION', ?, ?)", (f"LEDGER-{uuid.uuid4().hex[:12].upper()}", entitlement["id"], session["customer_id"], -consumed, ledger_request_id, now))
            self._conn.execute("INSERT INTO session_consumptions (id, session_id, entitlement_id, seconds, request_id, created_at) VALUES (?, ?, ?, ?, ?, ?)", (f"CONSUME-{uuid.uuid4().hex[:12].upper()}", session_id, entitlement["id"], consumed, payload.request_id, now))
            remaining -= consumed
            if remaining == 0:
                break
        if remaining:
            raise HTTPException(status_code=409, detail="Insufficient valid credit")
        self._conn.execute("UPDATE sessions SET consumed_seconds = consumed_seconds + ?, updated_at = ? WHERE id = ?", (payload.seconds, now, session_id))
        AuditService.record(
            self._conn, action="SESSION_CONSUMED", entity_type="SESSION", entity_id=session_id,
            request_id=payload.request_id, customer_id=session["customer_id"], amount=payload.seconds,
            new_value={"consumed_seconds": session["consumed_seconds"] + payload.seconds},
        )
        return self._response(self._conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone())

    def _event(self, session_id: str, event_type: str, reason: str | None, user_id: str, created_at: str) -> None:
        self._conn.execute(
            "INSERT INTO session_events (id, session_id, event_type, reason, user_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (f"EVENT-{uuid.uuid4().hex[:12].upper()}", session_id, event_type, reason, user_id, created_at),
        )