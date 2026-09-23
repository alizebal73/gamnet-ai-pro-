from fastapi import APIRouter, Depends

from gamenet.server.db import get_connection
from gamenet.server.models.credit import CreditBalanceResponse, CreditGrantRequest, CreditGrantResponse
from gamenet.server.security.auth import require_permission
from gamenet.server.services.credit_service import CreditService

router = APIRouter(prefix="/customers", tags=["credit"])


@router.get("/{customer_id}/credit", response_model=CreditBalanceResponse)
def get_credit(
    customer_id: str,
    _user: dict = Depends(require_permission("credit.view")),
) -> CreditBalanceResponse:
    with get_connection() as conn:
        return CreditService(conn).balance(customer_id)


@router.post("/{customer_id}/credit", response_model=CreditGrantResponse, status_code=201)
def grant_credit(
    customer_id: str,
    payload: CreditGrantRequest,
    _user: dict = Depends(require_permission("credit.grant")),
) -> CreditGrantResponse:
    with get_connection() as conn:
        return CreditService(conn).grant(customer_id, payload)