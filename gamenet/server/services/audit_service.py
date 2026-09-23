import json
import sqlite3
import uuid

from gamenet.server.db import utc_now_iso


class AuditService:
    @staticmethod
    def record(
        conn: sqlite3.Connection,
        *,
        action: str,
        entity_type: str,
        entity_id: str,
        request_id: str | None = None,
        user_id: str | None = None,
        customer_id: str | None = None,
        pc_id: str | None = None,
        reason: str | None = None,
        amount: int | None = None,
        old_value: object | None = None,
        new_value: object | None = None,
    ) -> None:
        conn.execute(
            """
            INSERT INTO audit_logs
                (id, timestamp, user_id, action, entity_type, entity_id, old_value,
                 new_value, amount, pc_id, customer_id, reason, request_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"AUDIT-{uuid.uuid4().hex[:12].upper()}", utc_now_iso(), user_id,
                action, entity_type, entity_id,
                json.dumps(old_value, sort_keys=True, default=str) if old_value is not None else None,
                json.dumps(new_value, sort_keys=True, default=str) if new_value is not None else None,
                amount, pc_id, customer_id, reason, request_id,
            ),
        )