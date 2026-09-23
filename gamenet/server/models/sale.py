from pydantic import BaseModel, Field


class SaleCreateRequest(BaseModel):
    customer_id: str = Field(min_length=1)
    item_type: str = Field(pattern="^(GAMING|PACKAGE|VIP|RECHARGE|FOOD|ACCESSORY)$")
    item_name: str = Field(min_length=1, max_length=200)
    duration_seconds: int = Field(default=0, ge=0, le=604800)
    amount: int | None = Field(default=None, gt=0)
    payment_method: str = Field(pattern="^(CASH|CARD|BALANCE|MIXED)$")
    request_id: str = Field(min_length=1, max_length=100)
    package_id: str | None = None
    vip_plan_id: str | None = None


class PaymentConfirmRequest(BaseModel):
    reference: str | None = Field(default=None, max_length=200)
    request_id: str = Field(min_length=1, max_length=100)


class PaymentResolutionRequest(BaseModel):
    status: str = Field(pattern="^(PAID|FAILED)$")
    reference: str | None = Field(default=None, max_length=200)
    request_id: str = Field(min_length=1, max_length=100)


class RefundRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)
    request_id: str = Field(min_length=1, max_length=100)


class SaleResponse(BaseModel):
    id: str
    customer_id: str
    item_type: str
    item_name: str
    duration_seconds: int
    amount: int
    status: str
    payment_id: str
    payment_status: str
    price_snapshot: int | None = None
    pricing_rule_id: str | None = None