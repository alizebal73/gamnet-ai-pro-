from pydantic import BaseModel, Field


class CreditGrantRequest(BaseModel):
    credit_type: str = Field(pattern="^(PAID|PACKAGE|PROMO|BONUS|ADMIN_ADJUSTMENT|REFUND_CREDIT)$")
    seconds: int = Field(gt=0, le=604800)
    source: str = Field(min_length=1, max_length=100)
    reason: str | None = Field(default=None, max_length=500)
    expires_at: str | None = None
    request_id: str = Field(min_length=1, max_length=100)


class CreditBalanceResponse(BaseModel):
    customer_id: str
    total_seconds: int


class CreditGrantResponse(BaseModel):
    entitlement_id: str
    customer_id: str
    credit_type: str
    granted_seconds: int
    total_seconds: int
    request_id: str