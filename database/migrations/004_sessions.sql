-- Migration 004: server-owned sessions and consumption events

CREATE TABLE IF NOT EXISTS sessions (
    id                TEXT PRIMARY KEY,
    customer_id       TEXT NOT NULL REFERENCES customers(id),
    pc_id             TEXT NOT NULL REFERENCES pcs(id),
    status            TEXT NOT NULL CHECK (status IN ('CREATED', 'ACTIVE', 'PAUSED', 'ENDED', 'CANCELLED', 'INTERRUPTED', 'CONNECTION_LOST')),
    consumed_seconds  INTEGER NOT NULL DEFAULT 0 CHECK (consumed_seconds >= 0),
    lease_id          TEXT,
    lease_expires_at  TEXT,
    started_at        TEXT,
    paused_at         TEXT,
    ended_at          TEXT,
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL,
    request_id        TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS session_events (
    id          TEXT PRIMARY KEY,
    session_id  TEXT NOT NULL REFERENCES sessions(id),
    event_type  TEXT NOT NULL,
    reason      TEXT,
    user_id     TEXT REFERENCES users(id),
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS session_consumptions (
    id               TEXT PRIMARY KEY,
    session_id       TEXT NOT NULL REFERENCES sessions(id),
    entitlement_id   TEXT NOT NULL REFERENCES entitlements(id),
    seconds          INTEGER NOT NULL CHECK (seconds > 0),
    request_id       TEXT NOT NULL,
    created_at       TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_one_active_session_customer
    ON sessions(customer_id) WHERE status IN ('CREATED', 'ACTIVE', 'PAUSED', 'CONNECTION_LOST');
CREATE UNIQUE INDEX IF NOT EXISTS idx_one_active_session_pc
    ON sessions(pc_id) WHERE status IN ('CREATED', 'ACTIVE', 'PAUSED', 'CONNECTION_LOST');
CREATE INDEX IF NOT EXISTS idx_session_events_session ON session_events(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_session_consumptions_request ON session_consumptions(request_id);

INSERT OR IGNORE INTO permissions (id, name, description)
VALUES ('PERM-SESSIONS-MANAGE', 'sessions.manage', 'Start, pause and end customer sessions');

INSERT OR IGNORE INTO role_permissions (role_id, permission_id, assigned_at)
SELECT r.id, p.id, strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
FROM roles r CROSS JOIN permissions p
WHERE r.name IN ('OWNER', 'MANAGER', 'OPERATOR') AND p.name = 'sessions.manage';