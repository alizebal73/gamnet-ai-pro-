```text
CREATED -> ACTIVE -> PAUSED -> ACTIVE
							|       |
							v       v
						ENDED  ENDED
```

Additional connection state is represented by lease expiry and Client Agent `PAUSED_BY_CONNECTION`. The Server freezes the session on expired lease; reconnect does not auto-resume. Session transfer and background recovery worker are pending.
