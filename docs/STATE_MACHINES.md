# GameNet Pro — State Machines

## Session

```text
CREATED → WAITING_PAYMENT → AUTHORIZED → ACTIVE → PAUSED → ENDED
```

Additional states: `INTERRUPTED`, `CANCELLED`, `TRANSFERRED`, `EXPIRED`, `CONNECTION_LOST`, `RESUMED` (transient).

Rules:
- One active session per customer (default).
- One active session per PC (default).
- State transitions validated **server-side** only.

## Payment

```text
CREATED → PENDING → PROCESSING → PAID
```

Terminal: `FAILED`, `CANCELLED`, `UNKNOWN`, `REFUND_PENDING`, `REFUNDED`.

Rules:
- **Payment First → Activation Second.**
- `UNKNOWN`: no immediate retry; inquiry required.
- Idempotent by `request_id`.

## PC

```text
OFFLINE → ONLINE → READY → BUSY → PAUSED
```

Also: `MAINTENANCE`, `ERROR`, `LOCKED`.

## VIP

```text
PENDING → ACTIVE → EXPIRED
```

Also: `CANCELLED`, `SUSPENDED`.

## Connection Loss Matrix

| Condition | Result |
|-----------|--------|
| Internet off, LAN on, Server on | Continue |
| LAN off | Pause |
| Server down | Pause all clients |
| Agent crash | Pause after timeout |
| PC restart | Recover + sync |
| Server restart | Pause → Sync → Manual Resume |
