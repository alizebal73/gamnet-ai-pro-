# API Overview

The server is the source of truth. Clients and Operator App use `/api/v1`; neither opens SQLite directly.

## Implemented

- `POST /api/v1/auth/login` and `GET /api/v1/auth/me`
- Customer CRUD/search under `/api/v1/customers`
- Customer login: `POST /api/v1/devices/{pc_id}/customer-login`
- Credit and balance: `/api/v1/customers/{customer_id}/credit` and `/balance`
- Pricing quote: `POST /api/v1/pricing/quote`
- Package catalog: `/api/v1/packages`
- VIP plan catalog: `/api/v1/vip/plans`
- Sales/payment confirmation/refund under `/api/v1/sales`
- Sessions under `/api/v1/sessions`
- Device REST heartbeat: `/api/v1/devices/{pc_id}/heartbeat`
- Device WebSocket: `/api/v1/ws/devices/{pc_id}`

## Authentication

Operator endpoints use `Authorization: Bearer <operator-session-token>`.
Device endpoints use `X-Device-Token`; Device authentication and Customer authentication are separate.

## WebSocket envelope

Messages use `message_type`, `message_id`, optional `request_id`, and `payload`.
The current implementation supports `AUTH`, `AUTH_ACK`, `HEARTBEAT`, and `HEARTBEAT_ACK`.

## Known gaps

- API error responses are not yet normalized to one error-code envelope.
- Token revoke/rotation endpoints are not implemented.
- WebSocket server push, command acknowledgements, and connection manager are pending.
