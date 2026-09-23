-- Migration 009: central idempotency records

CREATE TABLE IF NOT EXISTS idempotency_records (
    request_id  TEXT PRIMARY KEY,
    operation   TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id   TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_idempotency_entity
    ON idempotency_records(entity_type, entity_id);