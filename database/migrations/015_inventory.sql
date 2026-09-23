-- Migration 015: inventory items and stock ledger

CREATE TABLE IF NOT EXISTS inventory_items (
    id            TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    sku           TEXT NOT NULL UNIQUE,
    purchase_price INTEGER NOT NULL CHECK (purchase_price >= 0),
    sale_price    INTEGER NOT NULL CHECK (sale_price > 0),
    stock         INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    minimum_stock INTEGER NOT NULL DEFAULT 0 CHECK (minimum_stock >= 0),
    active        INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS inventory_transactions (
    id          TEXT PRIMARY KEY,
    item_id     TEXT NOT NULL REFERENCES inventory_items(id),
    delta_stock INTEGER NOT NULL CHECK (delta_stock <> 0),
    event_type  TEXT NOT NULL CHECK (event_type IN ('SALE', 'MANUAL_ADJUSTMENT', 'DAMAGE', 'LOSS', 'RETURN')),
    sale_id     TEXT REFERENCES sales(id),
    request_id  TEXT NOT NULL UNIQUE,
    reason      TEXT,
    created_at  TEXT NOT NULL
);

ALTER TABLE sales ADD COLUMN inventory_item_id TEXT REFERENCES inventory_items(id);

CREATE INDEX IF NOT EXISTS idx_inventory_transactions_item ON inventory_transactions(item_id, created_at);

INSERT OR IGNORE INTO permissions (id, name, description)
VALUES
    ('PERM-INVENTORY-VIEW', 'inventory.view', 'View inventory'),
    ('PERM-INVENTORY-MANAGE', 'inventory.manage', 'Manage inventory and stock');

INSERT OR IGNORE INTO role_permissions (role_id, permission_id, assigned_at)
SELECT r.id, p.id, strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
FROM roles r CROSS JOIN permissions p
WHERE (r.name IN ('OWNER', 'MANAGER', 'OPERATOR') AND p.name = 'inventory.view')
   OR (r.name IN ('OWNER', 'MANAGER') AND p.name = 'inventory.manage');