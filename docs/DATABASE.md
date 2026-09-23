# GameNet Pro — Database

## Engine

- SQLite 3 with **WAL mode**, **foreign keys ON**, transactional migrations.
- File: `data/gamenet.db` (configurable via `DATABASE_PATH`).

## Migration System

- SQL files in `database/migrations/` numbered `001_*.sql`, `002_*.sql`, ...
- Applied migrations tracked in `schema_migrations` table.
- Never edit applied migrations — add a new one.

## Migration 001 — Core Foundation

Creates:

| Table | Purpose |
|-------|---------|
| `schema_migrations` | Migration tracking |
| `settings` | Key-value store configuration |
| `users` | Operator/admin accounts |
| `roles` | Role definitions |
| `user_roles` | User ↔ role mapping |
| `customers` | Customer profiles |
| `customer_auth` | Hashed PIN/password |
| `pcs` | Registered gaming PCs |
| `device_credentials` | Per-PC device auth secrets (hashed) |
| `audit_logs` | Sensitive action audit trail |

Future migrations add: entitlements, sessions, sales, payments, inventory, shifts.

## Conventions

- Primary keys: `TEXT` UUIDs or prefixed IDs (`CUST-`, `PC-`, `SALE-`).
- Timestamps: `TEXT` UTC ISO-8601 (`2026-09-21T12:00:00Z`).
- Money: `INTEGER` in smallest currency unit (e.g. Rial).
- Duration/credit: `INTEGER` seconds.
- Soft delete: `status` column (`ACTIVE`, `INACTIVE`, `ARCHIVED`, `RETIRED`).

## Planned Tables (Master Spec §290)

Full list deferred to migration 002+:

`permissions`, `role_permissions`, `customer_balance_ledger`, `entitlements`, `entitlement_ledger`, `sessions`, `session_events`, `session_consumptions`, `sales`, `sale_items`, `payments`, `payment_transactions`, `pricing_rules`, `packages`, `vip_plans`, `shifts`, `inventory_*`, ...
