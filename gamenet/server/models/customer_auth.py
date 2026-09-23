from pydantic import BaseModel, Field


class CustomerLoginRequest(BaseModel):
    customer_number: int = Field(gt=0)
    pin: str = Field(min_length=4, max_length=72)


class CustomerLoginResponse(BaseModel):
    customer_id: str
    customer_number: int
    name: str
    gaming_credit_seconds: int
    active_session_id: str | None
    active_session_status: str | None