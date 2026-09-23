from pydantic import BaseModel, Field


class PackageCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    duration_seconds: int = Field(gt=0, le=604800)
    price: int = Field(gt=0)
    expiry_days: int | None = Field(default=None, gt=0, le=3650)
    bonus_seconds: int = Field(default=0, ge=0, le=604800)


class PackageResponse(BaseModel):
    id: str
    name: str
    duration_seconds: int
    price: int
    expiry_days: int | None
    bonus_seconds: int
    active: bool