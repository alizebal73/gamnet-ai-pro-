# Architectural Decisions

## ADR-001
Server is the Source of Truth.

## ADR-002
Client PCs never directly access central SQLite.

## ADR-003
Customer Credit is independent from PC Session.

## ADR-004
Session is independent from PC.

## ADR-005
Client/Server connection loss pauses active gaming after timeout.

## ADR-006
Internet outage alone does not pause if LAN to Server is healthy.

## ADR-007
Reconnect requires synchronization and manual resume by default.

## ADR-008
Payment must be verified before activating paid services.

## ADR-009
Financial history cannot be hard-deleted.

## ADR-010
One active Session per Customer by default.

## ADR-011
Important operations are idempotent.

## ADR-012
Server enforces permissions; UI hiding is not security.

## ADR-013
Credit uses a ledger/history model.

## ADR-014
Old transactions preserve historical price snapshots.

## ADR-015
Core LAN operation must not depend on ISP Internet.