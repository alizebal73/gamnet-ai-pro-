-- Migration 016: PC reservations

CREATE TABLE IF NOT EXISTS reservations (
    id          TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(id),
    pc_id       TEXT NOT NULL REFERENCES pcs(id),
    starts_at   TEXT NOT NULL,
    ends_at     TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'CANCELLED', 'EXPIRED', 'FULFILLED')),
    request_id  TEXT NOT NULL UNIQUE,
    created_at  TEXT NOT NULL,
    CHECK (ends_at > starts_at)
);

CREATE INDEX IF NOT EXISTS idx_reservations_pc_time ON reservations(pc_id, starts_at, ends_at, status);

INSERT OR IGNORE INTO permissions (id, name, description)
VALUES ('PERM-RESERVATIONS-MANAGE', 'reservations.manage', 'Manage PC reservations');

INSERT OR IGNORE INTO role_permissions (role_id, permission_id, assigned_at)
SELECT r.id, p.id, strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
FROM roles r CROSS JOIN permissions p
WHERE r.name IN ('OWNER', 'MANAGER', 'OPERATOR') AND p.name = 'reservations.manage';