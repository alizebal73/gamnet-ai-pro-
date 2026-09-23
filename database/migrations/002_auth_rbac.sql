-- Migration 002: authentication sessions and permissions

CREATE TABLE IF NOT EXISTS permissions (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id       TEXT NOT NULL REFERENCES roles(id),
    permission_id TEXT NOT NULL REFERENCES permissions(id),
    assigned_at   TEXT NOT NULL,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    token_hash TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    revoked_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_auth_sessions_user ON auth_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_expiry ON auth_sessions(expires_at);

INSERT OR IGNORE INTO roles (id, name, description, created_at)
VALUES
    ('ROLE-OWNER', 'OWNER', 'Full system access', strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    ('ROLE-MANAGER', 'MANAGER', 'Daily management access', strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    ('ROLE-OPERATOR', 'OPERATOR', 'Customer and sales operations', strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    ('ROLE-TECHNICIAN', 'TECHNICIAN', 'PC and maintenance operations', strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    ('ROLE-VIEWER', 'VIEWER', 'Read-only reporting access', strftime('%Y-%m-%dT%H:%M:%SZ', 'now'));

INSERT OR IGNORE INTO permissions (id, name, description)
VALUES
    ('PERM-CUSTOMERS-VIEW', 'customers.view', 'View customers'),
    ('PERM-CUSTOMERS-CREATE', 'customers.create', 'Create customers');

INSERT OR IGNORE INTO role_permissions (role_id, permission_id, assigned_at)
SELECT r.id, p.id, strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
FROM roles r CROSS JOIN permissions p
WHERE r.name IN ('OWNER', 'MANAGER')
   OR (r.name = 'OPERATOR' AND p.name IN ('customers.view', 'customers.create'));