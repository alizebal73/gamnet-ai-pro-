-- Migration 018: tamper-evident audit hash chain

ALTER TABLE audit_logs ADD COLUMN previous_hash TEXT;
ALTER TABLE audit_logs ADD COLUMN current_hash TEXT;

CREATE INDEX IF NOT EXISTS idx_audit_current_hash ON audit_logs(current_hash);