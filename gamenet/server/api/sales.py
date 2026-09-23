from fastapi import APIRouter, Depends

from gamenet.server.db import get_connection
from gamenet.server.models.sale import PaymentConfirmRequest, PaymentResolutionRequest, RefundRequest, SaleCreateRequest, SaleResponse
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


@router.post("/{sale_id}/unknown", response_model=SaleResponse)
def mark_payment_unknown(sale_id: str, payload: PaymentConfirmRequest, _user: dict = Depends(require_permission("payments.confirm"))) -> SaleResponse:
    with get_connection() as conn:
        return SaleService(conn).mark_unknown(sale_id, payload)


@router.post("/{sale_id}/resolve", response_model=SaleResponse)
def resolve_payment(sale_id: str, payload: PaymentResolutionRequest, _user: dict = Depends(require_permission("payments.confirm"))) -> SaleResponse:
    with get_connection() as conn:
        return SaleService(conn).resolve(sale_id, payload)


@router.post("/{sale_id}/refund", response_model=SaleResponse)
def request_refund(sale_id: str, payload: RefundRequest, user: dict = Depends(require_permission("payments.refund_request"))) -> SaleResponse:
    with get_connection() as conn:
        return SaleService(conn).request_refund(sale_id, payload, user["id"])


@router.post("/{sale_id}/refund/approve", response_model=SaleResponse)
def approve_refund(sale_id: str, payload: RefundRequest, user: dict = Depends(require_permission("payments.refund_approve"))) -> SaleResponse:
    with get_connection() as conn:
        return SaleService(conn).approve_refund(sale_id, payload, user["id"])