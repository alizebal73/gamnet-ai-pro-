from pydantic import BaseModel, Field


class InventoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    sku: str = Field(min_length=1, max_length=50)
    purchase_price: int = Field(ge=0)
    sale_price: int = Field(gt=0)
    initial_stock: int = Field(default=0, ge=0)
    minimum_stock: int = Field(default=0, ge=0)


class InventoryAdjustRequest(BaseModel):
    delta_stock: int
    reason: str = Field(min_length=1, max_length=500)
    request_id: str = Field(min_length=1, max_length=100)


class InventoryResponse(BaseModel):
    id: str
    name: str
    sku: str
    sale_price: int
    stock: int
    minimum_stock: int