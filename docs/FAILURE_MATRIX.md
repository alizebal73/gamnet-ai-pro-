| Failure | Current behavior | Status |
|---|---|---|
| Internet down, LAN healthy | REST/WebSocket LAN design does not depend on ISP | PARTIAL |
| Server unreachable | Client Agent enters `PAUSED_BY_CONNECTION` | PARTIAL |
| Lease expires | Server pauses session on next heartbeat | PARTIAL |
| Reconnect | Client remains paused and does not auto-resume | PARTIAL |
| Duplicate payment | Sale/payment state and request records prevent repeat activation | PARTIAL |
| Duplicate consumption | Consumption request ID is idempotent | PARTIAL |
| Duplicate refund | Refund state and request record prevent repeat refund | PARTIAL |
| Agent/UI crash | Agent core can recover on restart; Windows service is pending | UNTESTED |
| Server restart | Database migrations recover schema; session recovery worker is pending | MISSING |
| Database corruption | No safe mode/integrity recovery yet | MISSING |
| Disk full | No production policy yet | MISSING |
| Backup failure | Backup worker not implemented | MISSING |
| PC restart/power loss | State model preserves records; end-to-end recovery is pending | MISSING |
