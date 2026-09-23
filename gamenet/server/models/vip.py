from pydantic import BaseModel, Field


class VipPlanCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    duration_days: int = Field(gt=0, le=3650)
    price: int = Field(gt=0)
    discount_percent: int = Field(default=0, ge=0, le=100)


class VipPlanResponse(BaseModel):
    id: str
    name: str
    duration_days: int
    price: int
    discount_percent: int
    active: bool