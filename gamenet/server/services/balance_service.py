import sqlite3
import uuid

from fastapi import HTTPException

from gamenet.server.db import utc_now_iso
from gamenet.server.services.audit_service import AuditService


class BalanceService:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def balance(self, customer_id: str) -> int:
        row = self._conn.execute(
            "SELECT COALESCE(SUM(delta_amount), 0) AS amount FROM customer_balance_ledger WHERE customer_id = ?",
            (customer_id,),
        ).fetchone()
        return int(row["amount"])

    def apply(
        self,
        *,
        customer_id: str,
        delta_amount: int,
        event_type: str,
        request_id: str,
        sale_id: str | None = None,
        reason: str | None = None,
        actor_id: str | None = None,
    ) -> int:
        existing = self._conn.execute(
            "SELECT 1 FROM customer_balance_ledger WHERE request_id = ?", (request_id,)
        ).fetchone()
        if existing:
            return self.balance(customer_id)
        current = self.balance(customer_id)
        if current + delta_amount < 0:
            raise HTTPException(status_code=409, detail="Insufficient customer balance")
        now = utc_now_iso()
        self._conn.execute(
            """
            INSERT INTO customer_balance_ledger
                (id, customer_id, delta_amount, event_type, sale_id, request_id, reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (f"BALANCE-{uuid.uuid4().hex[:12].upper()}", customer_id, delta_amount,
             event_type, sale_id, request_id, reason, now),
        )
        AuditService.record(
            self._conn, action=f"BALANCE_{event_type}", entity_type="CUSTOMER_BALANCE",
            entity_id=customer_id, request_id=request_id, user_id=actor_id,
            customer_id=customer_id, amount=delta_amount, reason=reason,
            old_value={"amount": current}, new_value={"amount": current + delta_amount},
        )
        return current + delta_amount