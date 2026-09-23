-- Migration 006: refund permissions

INSERT OR IGNORE INTO permissions (id, name, description)
VALUES
    ('PERM-PAYMENTS-REFUND-REQUEST', 'payments.refund_request', 'Request a payment refund'),
    ('PERM-PAYMENTS-REFUND-APPROVE', 'payments.refund_approve', 'Approve a payment refund');

INSERT OR IGNORE INTO role_permissions (role_id, permission_id, assigned_at)
SELECT r.id, p.id, strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
FROM roles r CROSS JOIN permissions p
WHERE (r.name IN ('OWNER', 'MANAGER', 'OPERATOR') AND p.name = 'payments.refund_request')
   OR (r.name IN ('OWNER', 'MANAGER') AND p.name = 'payments.refund_approve');