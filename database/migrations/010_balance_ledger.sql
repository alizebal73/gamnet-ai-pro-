-- Migration 010: customer monetary balance ledger

CREATE TABLE IF NOT EXISTS customer_balance_ledger (
    id          TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(id),
    delta_amount INTEGER NOT NULL CHECK (delta_amount <> 0),
    event_type  TEXT NOT NULL CHECK (event_type IN ('RECHARGE', 'PURCHASE', 'ADJUSTMENT', 'REFUND')),
    sale_id     TEXT REFERENCES sales(id),
    request_id  TEXT NOT NULL UNIQUE,
    reason      TEXT,
    created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_balance_ledger_customer
    ON customer_balance_ledger(customer_id, created_at);