# GameNet Pro — Architecture

## Overview

```text
┌───────────────────────────────────────────┐
│              GAME NET SERVER              │
│  FastAPI + WebSocket + SQLite (WAL)       │
│  Auth | Customers | Sessions | Payments   │
└──────────────────┬────────────────────────┘
                   │ LAN REST / WebSocket
       ┌───────────┼───────────┐
    Client 01   Client 02   Client N
       │           │           │
    Operator/Admin App
```

## Layers (Server)

| Layer | Responsibility |
|-------|----------------|
| `api/` | HTTP/WebSocket routes, validation, auth middleware |
| `services/` | Business logic, state machines, orchestration |
| `repositories/` | SQL access only |
| `models/` | Pydantic schemas, domain types |
| `workers/` | Background jobs (expiry, recovery, backup) |
| `security/` | Auth, permissions, hashing |

## Source of Truth

Server owns: customers, PIN validity, balance, gaming credit, VIP, packages, payments, sessions, PC assignment, time consumed/remaining, pricing, transaction state.

Clients receive only what they need to display and operate the session UI.

## Connection & Session Rules

- Heartbeat ~1s (configurable).
- LAN loss → `PAUSED_BY_CONNECTION`, timer **frozen**.
- Internet loss with healthy LAN → session **continues**.
- Reconnect flow: Authenticate → Sync → Verify → **Manual Resume**.
- Session **lease** renewed via heartbeat; no lease → pause.

## Security Model

- **Device auth** (is this PC allowed?) separate from **customer auth** (is this player allowed?).
- Operator permissions enforced on server; UI hiding is not security.
- Audit log for sensitive actions; financial history never hard-deleted.

## Phases

See `TODO.md` and Master Spec §317.
