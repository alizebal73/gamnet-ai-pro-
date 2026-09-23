from fastapi import APIRouter, Depends

from gamenet.server.db import get_connection
from gamenet.server.models.pricing import PriceQuoteRequest, PriceQuoteResponse
from gamenet.server.security.auth import require_permission
from gamenet.server.services.pricing_service import PricingService

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.post("/quote", response_model=PriceQuoteResponse)
def quote_price(
    payload: PriceQuoteRequest,
    _user: dict = Depends(require_permission("sales.create")),
) -> PriceQuoteResponse:
    with get_connection() as conn:
        return PricingService(conn).quote(payload.item_type, payload.duration_seconds)