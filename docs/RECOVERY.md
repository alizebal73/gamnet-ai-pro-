# Recovery Plan

## Current guarantees

- Important records use SQLite transactions and migrations.
- Payment activation is performed only after payment confirmation.
- Credit and balance operations use idempotent ledger request IDs.
- Client heartbeat renews a session lease.
- An expired lease is paused on the next heartbeat.
- Client reconnect does not auto-resume a paused session.

## Current limitations

- There is no independent background worker that pauses leases while a client is fully offline.
- Server restart recovery and incomplete payment recovery are not implemented.
- Database integrity safe mode is not implemented.
- Backup, restore rehearsal, disk-full handling, and reconciliation workers are not implemented.

## Required next recovery work

1. Add a server worker that scans expired leases and writes a pause event.
2. Add startup integrity check and safe-mode state.
3. Add recovery records for incomplete payment, sale, entitlement, and session operations.
4. Add SQLite online backup and restore verification.
5. Add failure tests for server restart, client restart, power loss, and storage failure.
