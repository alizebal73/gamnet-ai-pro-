-- Migration 013: game catalog and per-device launch policy

CREATE TABLE IF NOT EXISTS games (
    id                  TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    slug                TEXT NOT NULL UNIQUE,
    platform            TEXT NOT NULL CHECK (platform IN ('WINDOWS', 'PS5', 'OTHER')),
    launch_type         TEXT NOT NULL CHECK (launch_type IN ('DIRECT_EXE', 'STEAM', 'EPIC', 'RIOT', 'ZULA', 'CUSTOM')),
    executable_path     TEXT,
    working_directory   TEXT,
    launch_arguments    TEXT,
    process_names       TEXT NOT NULL DEFAULT '[]',
    enabled             INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
    display_order       INTEGER NOT NULL DEFAULT 0,
    created_at          TEXT NOT NULL,
    updated_at          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS game_device_config (
    game_id             TEXT NOT NULL REFERENCES games(id),
    pc_id               TEXT NOT NULL REFERENCES pcs(id),
    enabled             INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
    executable_path     TEXT,
    working_directory   TEXT,
    launch_arguments    TEXT,
    updated_at          TEXT NOT NULL,
    PRIMARY KEY (game_id, pc_id)
);

INSERT OR IGNORE INTO permissions (id, name, description)
VALUES
    ('PERM-GAMES-VIEW', 'games.view', 'View available games'),
    ('PERM-GAMES-MANAGE', 'games.manage', 'Create and manage games');

INSERT OR IGNORE INTO role_permissions (role_id, permission_id, assigned_at)
SELECT r.id, p.id, strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
FROM roles r CROSS JOIN permissions p
WHERE (r.name IN ('OWNER', 'MANAGER', 'OPERATOR') AND p.name = 'games.view')
   OR (r.name IN ('OWNER', 'MANAGER') AND p.name = 'games.manage');