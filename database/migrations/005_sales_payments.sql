-- Migration 005: sales and payment state machine

CREATE TABLE IF NOT EXISTS sales (
    id               TEXT PRIMARY KEY,
    customer_id      TEXT NOT NULL REFERENCES customers(id),
    operator_id      TEXT NOT NULL REFERENCES users(id),
    item_type        TEXT NOT NULL CHECK (item_type IN ('GAMING', 'PACKAGE', 'VIP', 'RECHARGE', 'FOOD', 'ACCESSORY')),
    item_name        TEXT NOT NULL,
    duration_seconds INTEGER NOT NULL DEFAULT 0 CHECK (duration_seconds >= 0),
    amount           INTEGER NOT NULL CHECK (amount > 0),
    status           TEXT NOT NULL DEFAULT 'CREATED' CHECK (status IN ('CREATED', 'PAID', 'CANCELLED', 'REFUND_PENDING', 'REFUNDED')),
    request_id       TEXT NOT NULL UNIQUE,
    created_at       TEXT NOT NULL,
    updated_at       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS payments (
    id             TEXT PRIMARY KEY,
    sale_id        TEXT NOT NULL UNIQUE REFERENCES sales(id),
    method         TEXT NOT NULL CHECK (method IN ('CASH', 'CARD', 'BALANCE', 'MIXED')),
    amount         INTEGER NOT NULL CHECK (amount > 0),
    status         TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN ('CREATED', 'PENDING', 'PROCESSING', 'PAID', 'FAILED', 'CANCELLED', 'UNKNOWN', 'REFUND_PENDING', 'REFUNDED')),
    reference      TEXT,
    request_id     TEXT NOT NULL UNIQUE,
    created_at     TEXT NOT NULL,
    updated_at     TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id, created_at);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status, created_at);

INSERT OR IGNORE INTO permissions (id, name, description)
VALUES
    ('PERM-SALES-CREATE', 'sales.create', 'Create a sale'),
    ('PERM-PAYMENTS-CONFIRM', 'payments.confirm', 'Confirm a payment');

INSERT OR IGNORE INTO role_permissions (role_id, permission_id, assigned_at)
SELECT r.id, p.id, strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
FROM roles r CROSS JOIN permissions p
WHERE r.name IN ('OWNER', 'MANAGER', 'OPERATOR')
  AND p.name IN ('sales.create', 'payments.confirm');