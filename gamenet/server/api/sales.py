from fastapi import APIRouter, Depends

from gamenet.server.db import get_connection
from gamenet.server.models.sale import PaymentConfirmRequest, SaleCreateRequest, SaleResponse
from gamenet.server.security.auth import require_permission
from gamenet.server.services.sale_service import SaleService

router = APIRouter(prefix="/sales", tags=["sales"])


@router.post("", response_model=SaleResponse, status_code=201)
def create_sale(payload: SaleCreateRequest, user: dict = Depends(require_permission("sales.create"))) -> SaleResponse:
    with get_connection() as conn:
        return SaleService(conn).create(payload, user["id"])


@router.post("/{sale_id}/confirm", response_model=SaleResponse)
def confirm_payment(sale_id: str, payload: PaymentConfirmRequest, _user: dict = Depends(require_permission("payments.confirm"))) -> SaleResponse:
    with get_connection() as conn:
        return SaleService(conn).confirm(sale_id, payload)