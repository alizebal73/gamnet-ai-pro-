# CHANGELOG

## Unreleased

### Added
- Project documentation: `AGENTS.md`, `README_AI.md`, `docs/`
- Modular Python package `gamenet/` (server, shared, placeholders for operator/client)
- FastAPI server with health endpoint
- SQLite migration system and migration `001_initial.sql`
- Customer create/search/get API with bcrypt PIN hashing
- Test suite (`tests/test_health.py`, `tests/test_customers.py`)
- Authentication/RBAC, credit and balance ledgers, sessions, payments, pricing, packages, VIP, device heartbeat, WebSocket heartbeat, and PyQt Operator UI
- API, recovery, security, failure matrix, requirement matrix, and test-plan documentation

No production functionality should be considered complete solely because these documents exist.