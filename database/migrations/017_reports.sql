-- Migration 017: daily report permission

INSERT OR IGNORE INTO permissions (id, name, description)
VALUES ('PERM-REPORTS-VIEW', 'reports.view', 'View operational and financial reports');

INSERT OR IGNORE INTO role_permissions (role_id, permission_id, assigned_at)
SELECT r.id, p.id, strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
FROM roles r CROSS JOIN permissions p
WHERE r.name IN ('OWNER', 'MANAGER', 'VIEWER', 'OPERATOR') AND p.name = 'reports.view';