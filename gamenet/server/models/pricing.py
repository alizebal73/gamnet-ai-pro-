from pydantic import BaseModel, Field


class PriceQuoteRequest(BaseModel):
    item_type: str = Field(pattern="^(GAMING|PACKAGE|VIP|RECHARGE|FOOD|ACCESSORY)$")
    duration_seconds: int = Field(ge=0, le=604800)


class PriceQuoteResponse(BaseModel):
    item_type: str
    duration_seconds: int
    amount: int
    pricing_rule_id: str