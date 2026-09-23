-- Migration 003: customer gaming credit and immutable ledger

CREATE TABLE IF NOT EXISTS entitlements (
    id              TEXT PRIMARY KEY,
    customer_id     TEXT NOT NULL REFERENCES customers(id),
    credit_type     TEXT NOT NULL CHECK (credit_type IN ('PAID', 'PACKAGE', 'PROMO', 'BONUS', 'ADMIN_ADJUSTMENT', 'REFUND_CREDIT')),
    granted_seconds INTEGER NOT NULL CHECK (granted_seconds > 0),
    consumed_seconds INTEGER NOT NULL DEFAULT 0 CHECK (consumed_seconds >= 0 AND consumed_seconds <= granted_seconds),
    source          TEXT NOT NULL,
    expires_at      TEXT,
    status          TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'EXPIRED', 'EXHAUSTED', 'CANCELLED')),
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entitlement_ledger (
    id              TEXT PRIMARY KEY,
    entitlement_id  TEXT NOT NULL REFERENCES entitlements(id),
    customer_id     TEXT NOT NULL REFERENCES customers(id),
    delta_seconds   INTEGER NOT NULL CHECK (delta_seconds <> 0),
    event_type      TEXT NOT NULL CHECK (event_type IN ('GRANT', 'CONSUMPTION', 'ADJUSTMENT', 'REFUND', 'EXPIRY')),
    request_id      TEXT NOT NULL UNIQUE,
    reason          TEXT,
    created_at      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_entitlements_customer ON entitlements(customer_id, status, expires_at);
CREATE INDEX IF NOT EXISTS idx_entitlement_ledger_customer ON entitlement_ledger(customer_id, created_at);

INSERT OR IGNORE INTO permissions (id, name, description)
VALUES
    ('PERM-CREDIT-VIEW', 'credit.view', 'View customer credit'),
    ('PERM-CREDIT-GRANT', 'credit.grant', 'Grant or adjust customer credit');

INSERT OR IGNORE INTO role_permissions (role_id, permission_id, assigned_at)
SELECT r.id, p.id, strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
FROM roles r CROSS JOIN permissions p
WHERE r.name IN ('OWNER', 'MANAGER')
   OR (r.name = 'OPERATOR' AND p.name = 'credit.view');