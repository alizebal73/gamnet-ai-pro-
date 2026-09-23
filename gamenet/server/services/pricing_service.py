import sqlite3

from fastapi import HTTPException

from gamenet.server.models.pricing import PriceQuoteResponse


class PricingService:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def quote(self, item_type: str, duration_seconds: int) -> PriceQuoteResponse:
        row = self._conn.execute(
            """
            SELECT id, item_type, duration_seconds, amount
            FROM pricing_rules
            WHERE item_type = ? AND duration_seconds = ? AND active = 1
            """,
            (item_type, duration_seconds),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=422, detail="No active pricing rule for this service")
        return PriceQuoteResponse(
            item_type=row["item_type"], duration_seconds=row["duration_seconds"],
            amount=row["amount"], pricing_rule_id=row["id"],
        )