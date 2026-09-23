import sqlite3
import uuid

from gamenet.server.db import utc_now_iso


class CustomerRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def next_customer_number(self) -> int:
        row = self._conn.execute(
            "SELECT COALESCE(MAX(customer_number), 1039) + 1 AS n FROM customers"
        ).fetchone()
        return int(row["n"])

    def create(
        self,
        *,
        name: str,
        mobile: str | None,
        gaming_name: str | None,
        pin_hash: str,
    ) -> dict:
        customer_id = f"CUST-{uuid.uuid4().hex[:12].upper()}"
        customer_number = self.next_customer_number()
        now = utc_now_iso()

        self._conn.execute(
            """
            INSERT INTO customers (
                id, customer_number, name, mobile, gaming_name, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, 'ACTIVE', ?, ?)
            """,
            (customer_id, customer_number, name, mobile, gaming_name, now, now),
        )
        self._conn.execute(
            """
            INSERT INTO customer_auth (customer_id, pin_hash, failed_attempts, updated_at)
            VALUES (?, ?, 0, ?)
            """,
            (customer_id, pin_hash, now),
        )
        return self.get_by_id(customer_id)

    def get_by_id(self, customer_id: str) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM customers WHERE id = ?", (customer_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_by_number(self, customer_number: int) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM customers WHERE customer_number = ?", (customer_number,)
        ).fetchone()
        return dict(row) if row else None

    def search(self, query: str, limit: int = 50) -> list[dict]:
        pattern = f"%{query}%"
        rows = self._conn.execute(
            """
            SELECT * FROM customers
            WHERE status != 'ARCHIVED'
              AND (
                    CAST(customer_number AS TEXT) LIKE ?
                 OR name LIKE ?
                 OR COALESCE(mobile, '') LIKE ?
                 OR COALESCE(gaming_name, '') LIKE ?
              )
            ORDER BY customer_number
            LIMIT ?
            """,
            (pattern, pattern, pattern, pattern, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def count_active(self) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) AS c FROM customers WHERE status = 'ACTIVE'"
        ).fetchone()
        return int(row["c"])
