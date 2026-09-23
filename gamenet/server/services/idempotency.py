import sqlite3

from gamenet.server.db import utc_now_iso


def claim_request(
    conn: sqlite3.Connection,
    *,
    request_id: str,
    operation: str,
    entity_type: str,
    entity_id: str,
) -> bool:
    try:
        conn.execute(
            """
            INSERT INTO idempotency_records
                (request_id, operation, entity_type, entity_id, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (request_id, operation, entity_type, entity_id, utc_now_iso()),
        )
        return True
    except sqlite3.IntegrityError:
        return False