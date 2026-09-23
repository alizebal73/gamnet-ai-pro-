from pydantic import BaseModel, Field


class ReservationCreateRequest(BaseModel):
    customer_id: str = Field(min_length=1)
    pc_id: str = Field(min_length=1)
    starts_at: str
    ends_at: str
    request_id: str = Field(min_length=1, max_length=100)


class ReservationResponse(BaseModel):
    id: str
    customer_id: str
    pc_id: str
    starts_at: str
    ends_at: str
    status: str