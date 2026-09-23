from pydantic import BaseModel


class BalanceResponse(BaseModel):
    customer_id: str
    amount: int