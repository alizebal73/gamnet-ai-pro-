-- Migration 008: device heartbeat and client event history

CREATE TABLE IF NOT EXISTS client_events (
    id          TEXT PRIMARY KEY,
    pc_id       TEXT NOT NULL REFERENCES pcs(id),
    event_type  TEXT NOT NULL,
    agent_version TEXT,
    session_id  TEXT REFERENCES sessions(id),
    created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_client_events_pc ON client_events(pc_id, created_at);