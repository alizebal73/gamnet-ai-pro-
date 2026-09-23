import sqlite3
import uuid

from gamenet.server.db import utc_now_iso
from gamenet.server.models.credit import CreditGrantRequest, CreditGrantResponse, CreditBalanceResponse
from gamenet.server.services.audit_service import AuditService


class CreditService:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def balance(self, customer_id: str) -> CreditBalanceResponse:
        row = self._conn.execute(
            """
            SELECT COALESCE(SUM(granted_seconds - consumed_seconds), 0) AS total_seconds
            FROM entitlements
            WHERE customer_id = ? AND status = 'ACTIVE'
              AND (expires_at IS NULL OR expires_at > ?)
            """,
            (customer_id, utc_now_iso()),
        ).fetchone()
        return CreditBalanceResponse(customer_id=customer_id, total_seconds=int(row["total_seconds"]))

    def grant(self, customer_id: str, payload: CreditGrantRequest, actor_id: str | None = None) -> CreditGrantResponse:
        existing = self._conn.execute(
            "SELECT entitlement_id FROM entitlement_ledger WHERE request_id = ?", (payload.request_id,)
        ).fetchone()
        if existing:
            entitlement = self._conn.execute(
                "SELECT * FROM entitlements WHERE id = ?", (existing["entitlement_id"],)
            ).fetchone()
            balance = self.balance(customer_id)
            return CreditGrantResponse(
                entitlement_id=entitlement["id"], customer_id=customer_id,
                credit_type=entitlement["credit_type"], granted_seconds=entitlement["granted_seconds"],
                total_seconds=balance.total_seconds, request_id=payload.request_id,
            )

        now = utc_now_iso()
        entitlement_id = f"ENT-{uuid.uuid4().hex[:12].upper()}"
        self._conn.execute(
            """
            INSERT INTO entitlements
                (id, customer_id, credit_type, granted_seconds, source, expires_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (entitlement_id, customer_id, payload.credit_type, payload.seconds, payload.source,
             payload.expires_at, now, now),
        )
        self._conn.execute(
            """
            INSERT INTO entitlement_ledger
                (id, entitlement_id, customer_id, delta_seconds, event_type, request_id, reason, created_at)
            VALUES (?, ?, ?, ?, 'GRANT', ?, ?, ?)
            """,
            (f"LEDGER-{uuid.uuid4().hex[:12].upper()}", entitlement_id, customer_id,
             payload.seconds, payload.request_id, payload.reason, now),
        )
        AuditService.record(
            self._conn, action="CREDIT_GRANTED", entity_type="ENTITLEMENT", entity_id=entitlement_id,
            request_id=payload.request_id, user_id=actor_id, customer_id=customer_id,
            amount=payload.seconds, reason=payload.reason,
            new_value={"credit_type": payload.credit_type, "seconds": payload.seconds},
        )
        balance = self.balance(customer_id)
        return CreditGrantResponse(
            entitlement_id=entitlement_id, customer_id=customer_id,
            credit_type=payload.credit_type, granted_seconds=payload.seconds,
            total_seconds=balance.total_seconds, request_id=payload.request_id,
        )