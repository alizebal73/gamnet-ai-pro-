from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query

from gamenet.server.db import get_connection
from gamenet.server.models.report import DailyReportResponse
from gamenet.server.security.auth import require_permission

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/daily", response_model=DailyReportResponse)
def daily_report(
    day: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    _user: dict = Depends(require_permission("reports.view")),
) -> DailyReportResponse:
    report_day = day or datetime.now(UTC).date().isoformat()
    with get_connection() as conn:
        revenue = conn.execute("SELECT COALESCE(SUM(amount), 0) AS value, COUNT(*) AS count FROM sales WHERE status = 'PAID' AND substr(created_at, 1, 10) = ?", (report_day,)).fetchone()
        types = conn.execute("SELECT item_type, COALESCE(SUM(amount), 0) AS value FROM sales WHERE status = 'PAID' AND substr(created_at, 1, 10) = ? GROUP BY item_type", (report_day,)).fetchall()
        sessions = conn.execute("SELECT COUNT(*) AS count, COALESCE(SUM(consumed_seconds), 0) AS seconds FROM sessions WHERE substr(created_at, 1, 10) = ?", (report_day,)).fetchone()
        payments = conn.execute("SELECT method, COALESCE(SUM(amount), 0) AS value FROM payments WHERE status = 'PAID' AND substr(created_at, 1, 10) = ? GROUP BY method", (report_day,)).fetchall()
        unknown = conn.execute("SELECT COUNT(*) AS count FROM payments WHERE status = 'UNKNOWN' AND substr(created_at, 1, 10) = ?", (report_day,)).fetchone()["count"]
        difference = conn.execute("SELECT COALESCE(SUM(difference), 0) AS value FROM shifts WHERE status = 'CLOSED' AND substr(closed_at, 1, 10) = ?", (report_day,)).fetchone()["value"]
    by_type = {row["item_type"]: row["value"] for row in types}
    by_method = {row["method"]: row["value"] for row in payments}
    return DailyReportResponse(
        day=report_day, revenue=revenue["value"], sales_count=revenue["count"],
        sessions_count=sessions["count"], gaming_seconds=sessions["seconds"],
        vip_revenue=by_type.get("VIP", 0), package_revenue=by_type.get("PACKAGE", 0),
        food_revenue=by_type.get("FOOD", 0), cash_revenue=by_method.get("CASH", 0),
        card_revenue=by_method.get("CARD", 0), unknown_payments=unknown,
        cash_difference=difference,
    )