-- Migration 007: server-owned pricing rules and historical snapshots

CREATE TABLE IF NOT EXISTS pricing_rules (
    id               TEXT PRIMARY KEY,
    item_type        TEXT NOT NULL CHECK (item_type IN ('GAMING', 'PACKAGE', 'VIP', 'RECHARGE', 'FOOD', 'ACCESSORY')),
    duration_seconds INTEGER NOT NULL CHECK (duration_seconds >= 0),
    amount           INTEGER NOT NULL CHECK (amount > 0),
    active           INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    created_at       TEXT NOT NULL,
    updated_at       TEXT NOT NULL,
    UNIQUE (item_type, duration_seconds)
);

ALTER TABLE sales ADD COLUMN pricing_rule_id TEXT REFERENCES pricing_rules(id);
ALTER TABLE sales ADD COLUMN price_snapshot INTEGER;

INSERT OR IGNORE INTO pricing_rules
    (id, item_type, duration_seconds, amount, created_at, updated_at)
VALUES
    ('PRICE-GAMING-900', 'GAMING', 900, 20000, strftime('%Y-%m-%dT%H:%M:%SZ', 'now'), strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    ('PRICE-GAMING-1800', 'GAMING', 1800, 40000, strftime('%Y-%m-%dT%H:%M:%SZ', 'now'), strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    ('PRICE-GAMING-3600', 'GAMING', 3600, 80000, strftime('%Y-%m-%dT%H:%M:%SZ', 'now'), strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    ('PRICE-GAMING-7200', 'GAMING', 7200, 150000, strftime('%Y-%m-%dT%H:%M:%SZ', 'now'), strftime('%Y-%m-%dT%H:%M:%SZ', 'now'));