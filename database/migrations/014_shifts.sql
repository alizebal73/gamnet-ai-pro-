-- Migration 014: operator shifts and cash movements

CREATE TABLE IF NOT EXISTS shifts (
    id            TEXT PRIMARY KEY,
    user_id       TEXT NOT NULL REFERENCES users(id),
    status        TEXT NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'CLOSED')),
    opening_cash  INTEGER NOT NULL CHECK (opening_cash >= 0),
    expected_cash INTEGER,
    actual_cash   INTEGER,
    difference    INTEGER,
    opened_at     TEXT NOT NULL,
    closed_at     TEXT,
    close_reason  TEXT
);

CREATE TABLE IF NOT EXISTS cash_movements (
    id          TEXT PRIMARY KEY,
    shift_id    TEXT NOT NULL REFERENCES shifts(id),
    delta_amount INTEGER NOT NULL CHECK (delta_amount <> 0),
    event_type  TEXT NOT NULL CHECK (event_type IN ('SALE', 'REFUND', 'CASH_IN', 'CASH_OUT', 'ADJUSTMENT')),
    sale_id     TEXT REFERENCES sales(id),
    request_id  TEXT NOT NULL UNIQUE,
    reason      TEXT,
    created_at  TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_one_open_shift_user ON shifts(user_id) WHERE status = 'OPEN';
CREATE INDEX IF NOT EXISTS idx_cash_movements_shift ON cash_movements(shift_id, created_at);

INSERT OR IGNORE INTO permissions (id, name, description)
VALUES ('PERM-SHIFTS-MANAGE', 'shifts.manage', 'Open and close operator shifts');

INSERT OR IGNORE INTO role_permissions (role_id, permission_id, assigned_at)
SELECT r.id, p.id, strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
FROM roles r CROSS JOIN permissions p
WHERE r.name IN ('OWNER', 'MANAGER', 'OPERATOR') AND p.name = 'shifts.manage';