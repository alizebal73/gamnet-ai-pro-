from gamenet.server.db import get_connection
from gamenet.server.services.recovery_service import RecoveryService


def test_recovery_pauses_expired_lease_and_checks_integrity():
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO pcs (id, device_code, display_name, status, created_at, updated_at) VALUES ('PC-RECOVERY-01', 'PC-RECOVERY-01', 'Recovery PC', 'BUSY', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO customers (id, customer_number, name, status, created_at, updated_at) VALUES ('CUST-RECOVERY-01', 900001, 'Recovery Customer', 'ACTIVE', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO sessions (id, customer_id, pc_id, status, lease_id, lease_expires_at, created_at, updated_at, request_id) VALUES ('SESSION-RECOVERY-01', 'CUST-RECOVERY-01', 'PC-RECOVERY-01', 'ACTIVE', 'LEASE-RECOVERY-01', '2020-01-01T00:00:00Z', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z', 'RECOVERY-SESSION-1')"
        )
        paused = RecoveryService.pause_expired_leases(conn)
        status = conn.execute("SELECT status FROM sessions WHERE id = 'SESSION-RECOVERY-01'").fetchone()["status"]
        assert paused == 1
        assert status == "PAUSED"
        assert RecoveryService.integrity_ok(conn) is True