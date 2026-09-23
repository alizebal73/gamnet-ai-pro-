from pydantic import BaseModel


class DailyReportResponse(BaseModel):
    day: str
    revenue: int
    sales_count: int
    sessions_count: int
    gaming_seconds: int
    vip_revenue: int
    package_revenue: int
    food_revenue: int
    cash_revenue: int
    card_revenue: int
    unknown_payments: int
    cash_difference: int