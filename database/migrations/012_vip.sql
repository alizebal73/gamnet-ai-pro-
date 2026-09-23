-- Migration 012: VIP plans and customer VIP entitlements

CREATE TABLE IF NOT EXISTS vip_plans (
    id               TEXT PRIMARY KEY,
    name             TEXT NOT NULL UNIQUE,
    duration_days    INTEGER NOT NULL CHECK (duration_days > 0),
    price            INTEGER NOT NULL CHECK (price > 0),
    discount_percent INTEGER NOT NULL DEFAULT 0 CHECK (discount_percent BETWEEN 0 AND 100),
    active           INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    created_at       TEXT NOT NULL,
    updated_at       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS customer_vip (
    id          TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(id),
    plan_id     TEXT NOT NULL REFERENCES vip_plans(id),
    sale_id     TEXT NOT NULL UNIQUE REFERENCES sales(id),
    starts_at   TEXT NOT NULL,
    expires_at  TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('PENDING', 'ACTIVE', 'EXPIRED', 'CANCELLED')),
    created_at  TEXT NOT NULL
);

ALTER TABLE sales ADD COLUMN vip_plan_id TEXT REFERENCES vip_plans(id);

CREATE INDEX IF NOT EXISTS idx_customer_vip_customer ON customer_vip(customer_id, status, expires_at);

INSERT OR IGNORE INTO permissions (id, name, description)
VALUES
    ('PERM-VIP-VIEW', 'vip.view', 'View VIP plans and status'),
    ('PERM-VIP-MANAGE', 'vip.manage', 'Create and manage VIP plans');

INSERT OR IGNORE INTO role_permissions (role_id, permission_id, assigned_at)
SELECT r.id, p.id, strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
FROM roles r CROSS JOIN permissions p
WHERE (r.name IN ('OWNER', 'MANAGER', 'OPERATOR') AND p.name = 'vip.view')
   OR (r.name IN ('OWNER', 'MANAGER') AND p.name = 'vip.manage');