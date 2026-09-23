# Requirement Matrix Snapshot

This is a factual snapshot of the current implementation, not a claim of final completion.

| Requirement | Status | Evidence / note |
|---|---|---|
| Server is source of truth | PARTIAL | FastAPI server owns current customer, credit, session, payment and device APIs |
| Client does not open SQLite | DONE | Client Agent and Operator API use HTTP/WebSocket |
| Operator authentication and RBAC | PARTIAL | Basic roles, permissions and bearer sessions exist |
| Customer PIN hashing and lockout | PARTIAL | bcrypt hashing and temporary lockout exist |
| Credit entitlement ledger | PARTIAL | Entitlements and consumption ledger exist; rebuild tooling is pending |
| Monetary balance ledger | PARTIAL | Recharge and BALANCE debit now use a ledger |
| Payment-first activation | PARTIAL | Gaming, Package and VIP activation follow payment confirmation |
| Pricing snapshot | PARTIAL | Basic server pricing rules and snapshots exist |
| Audit trail | PARTIAL | Central service records core operations; full coverage and hash chain are pending |
| Session lease/manual resume | PARTIAL | REST/WebSocket heartbeat and lease pause exist; worker recovery is pending |
| WebSocket protocol | PARTIAL | Device AUTH and HEARTBEAT are implemented; push/commands are pending |
| Package domain | PARTIAL | Catalog, expiry and entitlement activation exist |
| VIP domain | PARTIAL | Plan and activation exist; renewal rules/history are pending |
| Client Agent | PARTIAL | Testable HTTP heartbeat core exists; Windows service is pending |
| Operator App | PARTIAL | PyQt quick-sale UI exists; dashboard, shifts and reports are pending |
| Client UI | MISSING | Customer API exists, but customer PyQt UI is pending |
| Game catalog/launch/process monitor | MISSING | Not implemented |
| Kiosk/Lockdown | MISSING | Windows policy/service integration is not implemented |
| Inventory | PARTIAL | Catalog, stock ledger and sale decrement exist; reconciliation and purchase workflow are pending |
| Shifts | PARTIAL | Open/close and cash difference exist; automatic cash movement from all sales is pending |
| Reservations | PARTIAL | PC reservation and overlap detection exist; queue/no-show/fulfillment workflow is pending |
| Reports/alerts/reconciliation | MISSING | Not implemented |
| Backup/restore/installer | MISSING | Not implemented |
