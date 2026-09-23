from gamenet.server.db import get_connection
from gamenet.server.services.audit_service import AuditService


def test_audit_records_form_a_hash_chain():
    with get_connection() as conn:
        AuditService.record(conn, action="TEST_ONE", entity_type="TEST", entity_id="1")
        AuditService.record(conn, action="TEST_TWO", entity_type="TEST", entity_id="2")
        rows = conn.execute(
            "SELECT previous_hash, current_hash FROM audit_logs WHERE action IN ('TEST_ONE', 'TEST_TWO') ORDER BY timestamp, id"
        ).fetchall()

    assert len(rows) == 2
    assert rows[0]["previous_hash"]
    assert rows[0]["current_hash"]
    assert rows[1]["previous_hash"] == rows[0]["current_hash"]
    assert rows[1]["current_hash"] != rows[0]["current_hash"]