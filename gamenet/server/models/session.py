from pydantic import BaseModel, Field


class SessionStartRequest(BaseModel):
    customer_id: str = Field(min_length=1)
    pc_id: str = Field(min_length=1)
    request_id: str = Field(min_length=1, max_length=100)


class SessionActionRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)
    request_id: str = Field(min_length=1, max_length=100)


class SessionConsumeRequest(BaseModel):
    seconds: int = Field(gt=0, le=3600)
    request_id: str = Field(min_length=1, max_length=100)


class SessionResponse(BaseModel):
    id: str
    customer_id: str
    pc_id: str
    status: str
    consumed_seconds: int
    lease_id: str | None
    lease_expires_at: str | None