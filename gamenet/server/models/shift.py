from pydantic import BaseModel, Field


class ShiftOpenRequest(BaseModel):
    opening_cash: int = Field(ge=0)
    request_id: str = Field(min_length=1, max_length=100)


class ShiftCloseRequest(BaseModel):
    actual_cash: int = Field(ge=0)
    reason: str | None = Field(default=None, max_length=500)
    request_id: str = Field(min_length=1, max_length=100)


class ShiftResponse(BaseModel):
    id: str
    user_id: str
    status: str
    opening_cash: int
    expected_cash: int | None
    actual_cash: int | None
    difference: int | None