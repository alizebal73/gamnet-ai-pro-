import sqlite3
import uuid

from gamenet.server.db import utc_now_iso


class RecoveryService:
    @staticmethod
    def pause_expired_leases(conn: sqlite3.Connection) -> int:
        now = utc_now_iso()
        sessions = conn.execute(
            "SELECT id FROM sessions WHERE status = 'ACTIVE' AND lease_expires_at IS NOT NULL AND lease_expires_at <= ?",
            (now,),
        ).fetchall()
        for session in sessions:
            conn.execute(
                "UPDATE sessions SET status = 'PAUSED', paused_at = ?, updated_at = ? WHERE id = ? AND status = 'ACTIVE'",
                (now, now, session["id"]),
            )
            conn.execute(
                "INSERT INTO session_events (id, session_id, event_type, reason, created_at) VALUES (?, ?, 'LEASE_EXPIRED', 'Recovery scan expired lease', ?)",
                (f"EVENT-{uuid.uuid4().hex[:12].upper()}", session["id"], now),
            )
        return len(sessions)

    @staticmethod
    def integrity_ok(conn: sqlite3.Connection) -> bool:
        return conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"