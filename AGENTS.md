# GameNet Pro — Agent Rules

## Mission

Transform GameNet Pro into a **GameNet Operating System**: Server is Source of Truth; Client never touches SQLite directly.

## Non-Negotiable Rules

1. **Server → Database only.** Clients and Operator App talk to Server API/WebSocket, never to SQLite files.
2. **Credit ≠ Session ≠ PC.** Time belongs to Customer/Entitlement, not to a PC.
3. **Payment First → Activation Second.** No VIP/time/balance without verified payment (or authorized override with audit).
4. **Manual Resume after reconnect** by default (`AUTO_RESUME=false`).
5. **Ledger model** for credit and balance — never direct field edits.
6. **Server-side enforcement** of permissions, session rules, and pricing.
7. **Idempotent** important operations (Request ID).
8. **No hard-delete** of financial history.
9. **Modular code** — no giant single-file apps.
10. **Minimal diff** — match existing conventions; do not over-engineer.

## Stack

- Python 3.13+
- FastAPI + Uvicorn (Server)
- PyQt6 (Operator App, Client UI — later phases)
- SQLite (WAL, FK, migrations)
- PyInstaller (deployment — later)

## Project Layout

```text
gamenet/
├── server/       api, services, repositories, models, workers, security
├── operator_app/   (Phase 3)
├── client_agent/   (Phase 2)
└── shared/         enums, protocol, validators
database/migrations/
tests/
docs/
```

## Development Order

See `TODO.md` and `docs/ARCHITECTURE.md`. Core first: Customer, Credit, Session, Payment, Server, Client connection, Recovery.

## Key Documents

- `docs/MASTER_SPEC.md` — full specification (350 sections)
- `docs/ARCHITECTURE.md` — architecture summary
- `docs/DATABASE.md` — schema and migration notes
- `docs/STATE_MACHINES.md` — session, payment, PC states
- `DECISIONS.md` — ADR-001..015

## Before Coding

1. Read relevant docs section.
2. Check ADRs in `DECISIONS.md`.
3. Add migration for schema changes.
4. Add tests for business logic.
5. Update `CHANGELOG.md`.
