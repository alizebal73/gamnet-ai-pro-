-- Migration 001: Core foundation tables
-- GameNet Pro

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version     INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    applied_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id              TEXT PRIMARY KEY,
    username        TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    display_name    TEXT,
    status          TEXT NOT NULL DEFAULT 'ACTIVE'
                    CHECK (status IN ('ACTIVE', 'INACTIVE', 'ARCHIVED')),
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS roles (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_roles (
    user_id     TEXT NOT NULL REFERENCES users(id),
    role_id     TEXT NOT NULL REFERENCES roles(id),
    assigned_at TEXT NOT NULL,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS customers (
    id              TEXT PRIMARY KEY,
    customer_number INTEGER NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    mobile          TEXT,
    gaming_name     TEXT,
    status          TEXT NOT NULL DEFAULT 'ACTIVE'
                    CHECK (status IN ('ACTIVE', 'INACTIVE', 'ARCHIVED')),
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS customer_auth (
    customer_id     TEXT PRIMARY KEY REFERENCES customers(id),
    pin_hash        TEXT NOT NULL,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until    TEXT,
    updated_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pcs (
    id              TEXT PRIMARY KEY,
    device_code     TEXT NOT NULL UNIQUE,
    display_name    TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'OFFLINE'
                    CHECK (status IN (
                        'OFFLINE', 'ONLINE', 'READY', 'BUSY', 'PAUSED',
                        'MAINTENANCE', 'ERROR', 'LOCKED', 'RETIRED'
                    )),
    agent_version   TEXT,
    last_seen_at    TEXT,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS device_credentials (
    pc_id           TEXT PRIMARY KEY REFERENCES pcs(id),
    secret_hash     TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    rotated_at      TEXT
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id              TEXT PRIMARY KEY,
    timestamp       TEXT NOT NULL,
    user_id         TEXT REFERENCES users(id),
    role_name       TEXT,
    action          TEXT NOT NULL,
    entity_type     TEXT,
    entity_id       TEXT,
    old_value       TEXT,
    new_value       TEXT,
    amount          INTEGER,
    pc_id           TEXT REFERENCES pcs(id),
    customer_id     TEXT REFERENCES customers(id),
    reason          TEXT,
    request_id      TEXT,
    ip_address      TEXT
);

CREATE INDEX IF NOT EXISTS idx_customers_number ON customers(customer_number);
CREATE INDEX IF NOT EXISTS idx_customers_mobile ON customers(mobile);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_pcs_device_code ON pcs(device_code);
