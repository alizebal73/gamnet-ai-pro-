-- Migration 011: package catalog and sale traceability

CREATE TABLE IF NOT EXISTS packages (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    duration_seconds INTEGER NOT NULL CHECK (duration_seconds > 0),
    price           INTEGER NOT NULL CHECK (price > 0),
    expiry_days     INTEGER CHECK (expiry_days IS NULL OR expiry_days > 0),
    bonus_seconds   INTEGER NOT NULL DEFAULT 0 CHECK (bonus_seconds >= 0),
    active          INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

ALTER TABLE sales ADD COLUMN package_id TEXT REFERENCES packages(id);

INSERT OR IGNORE INTO permissions (id, name, description)
VALUES
    ('PERM-PACKAGES-VIEW', 'packages.view', 'View package catalog'),
    ('PERM-PACKAGES-MANAGE', 'packages.manage', 'Create and manage packages');

INSERT OR IGNORE INTO role_permissions (role_id, permission_id, assigned_at)
SELECT r.id, p.id, strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
FROM roles r CROSS JOIN permissions p
WHERE (r.name IN ('OWNER', 'MANAGER', 'OPERATOR') AND p.name = 'packages.view')
   OR (r.name IN ('OWNER', 'MANAGER') AND p.name = 'packages.manage');