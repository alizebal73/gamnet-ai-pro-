from fastapi import APIRouter, Depends, HTTPException, Query

from gamenet.server.db import get_connection
from gamenet.server.models.schemas import (
    CustomerCreate,
    CustomerListResponse,
    CustomerResponse,
)
from gamenet.server.services.customer_service import CustomerService
from gamenet.server.security.auth import require_permission

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer(
    payload: CustomerCreate,
    _user: dict = Depends(require_permission("customers.create")),
) -> CustomerResponse:
    with get_connection() as conn:
        service = CustomerService(conn)
        return service.create_customer(payload)


@router.get("/search", response_model=CustomerListResponse)
def search_customers(
    q: str = Query(min_length=1),
    _user: dict = Depends(require_permission("customers.view")),
) -> CustomerListResponse:
    with get_connection() as conn:
        service = CustomerService(conn)
        items = service.search(q)
        return CustomerListResponse(items=items, total=len(items))


@router.get("/by-number/{customer_number}", response_model=CustomerResponse)
def get_customer_by_number(
    customer_number: int,
    _user: dict = Depends(require_permission("customers.view")),
) -> CustomerResponse:
    with get_connection() as conn:
        service = CustomerService(conn)
        customer = service.get_by_number(customer_number)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: str,
    _user: dict = Depends(require_permission("customers.view")),
) -> CustomerResponse:
    with get_connection() as conn:
        service = CustomerService(conn)
        customer = service.get_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
