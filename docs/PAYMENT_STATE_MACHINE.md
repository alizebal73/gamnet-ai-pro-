```text
CREATED -> PENDING -> PROCESSING -> PAID
								 |            |
								 v            v
							 UNKNOWN     REFUND_PENDING -> REFUNDED
								 |
								 +-> FAILED
```

Payment confirmation is idempotent. `UNKNOWN` must be resolved before activation. Gaming, Package and VIP activation happens only after `PAID`.
