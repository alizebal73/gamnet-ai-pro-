# Test Plan

## Current automated coverage

The suite covers operator authentication, customer CRUD/search, Customer PIN lockout, credit grant and consumption, balance recharge/debit, package and VIP activation, pricing snapshots, payment-first activation, UNKNOWN payment, refund approval, session lifecycle, lease expiry, Device heartbeat, Customer/Device authentication separation, Client Agent connection loss, Operator API client, and Device WebSocket AUTH/HEARTBEAT.

## Current result

Run:

```text
PYTHONPATH=. pytest -q
```

The current suite has 26 passing tests. FastAPI lifecycle deprecation warnings remain and are tracked separately.

## Required failure tests before production

- LAN down and reconnect
- Server down and restart
- Agent crash and UI crash
- PC restart and power loss
- Clock change and clock drift
- Concurrent session/payment/refund requests
- Database integrity failure and disk-full behavior
- Backup failure and restore rehearsal
- Unauthorized process and kiosk escape attempts
- Game launch failure, crash, and server disconnect
