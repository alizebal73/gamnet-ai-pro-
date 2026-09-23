## Current security model

- The Server is authoritative for customer, entitlement, session, payment and pricing state.
- Operator authentication uses bcrypt password hashes and expiring bearer sessions.
- Customer PIN authentication is separate from Device authentication.
- Device credentials are stored as hashes and are sent in the `X-Device-Token` header.
- Sensitive operations use server-side permission checks and central audit records.
- Financial and credit operations use integer amounts/seconds and idempotent request IDs.

## Current limitations

- Token revocation and device credential rotation endpoints are pending.
- Audit hash chaining, security event dashboard, TLS deployment, and secret storage are pending.
- Windows kiosk enforcement and process tamper detection are not implemented.
- WebSocket command authorization and remote command audit are pending.

Never treat the Client UI, IP address, MAC address, Windows clock, or cached credit as trusted authority.
