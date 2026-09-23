import json
import hashlib
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
        previous = conn.execute(
            "SELECT current_hash FROM audit_logs ORDER BY timestamp DESC, id DESC LIMIT 1"
        ).fetchone()
        previous_hash = previous["current_hash"] if previous and previous["current_hash"] else "GENESIS"
        audit_id = f"AUDIT-{uuid.uuid4().hex[:12].upper()}"
        timestamp = utc_now_iso()
        hash_payload = {
            "id": audit_id, "timestamp": timestamp, "user_id": user_id, "action": action,
            "entity_type": entity_type, "entity_id": entity_id, "request_id": request_id,
            "customer_id": customer_id, "pc_id": pc_id, "amount": amount,
            "reason": reason, "old_value": old_value, "new_value": new_value,
        }
        current_hash = hashlib.sha256(
            f"{previous_hash}:{json.dumps(hash_payload, sort_keys=True, default=str)}".encode("utf-8")
        ).hexdigest()
        conn.execute(
            """
            INSERT INTO audit_logs
                (id, timestamp, user_id, action, entity_type, entity_id, old_value,
                 new_value, amount, pc_id, customer_id, reason, request_id, previous_hash, current_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                audit_id, timestamp, user_id,
                action, entity_type, entity_id,
                json.dumps(old_value, sort_keys=True, default=str) if old_value is not None else None,
                json.dumps(new_value, sort_keys=True, default=str) if new_value is not None else None,
                amount, pc_id, customer_id, reason, request_id, previous_hash, current_hash,
            ),
        )