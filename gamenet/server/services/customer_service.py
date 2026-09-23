import sqlite3

from gamenet.server.models.schemas import CustomerCreate, CustomerResponse
from gamenet.server.repositories.customer_repository import CustomerRepository
from gamenet.server.security.passwords import hash_secret


class CustomerService:
    def __init__(self, conn: sqlite3.Connection):
        self._repo = CustomerRepository(conn)

    @staticmethod
    def _to_response(row: dict) -> CustomerResponse:
        return CustomerResponse(
            id=row["id"],
            customer_number=row["customer_number"],
            name=row["name"],
            mobile=row["mobile"],
            gaming_name=row["gaming_name"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create_customer(self, payload: CustomerCreate) -> CustomerResponse:
        pin_hash = hash_secret(payload.pin)
        row = self._repo.create(
            name=payload.name.strip(),
            mobile=payload.mobile.strip() if payload.mobile else None,
            gaming_name=payload.gaming_name.strip() if payload.gaming_name else None,
            pin_hash=pin_hash,
        )
        return self._to_response(row)

    def get_by_number(self, customer_number: int) -> CustomerResponse | None:
        row = self._repo.get_by_number(customer_number)
        return self._to_response(row) if row else None

    def get_by_id(self, customer_id: str) -> CustomerResponse | None:
        row = self._repo.get_by_id(customer_id)
        return self._to_response(row) if row else None

    def search(self, query: str) -> list[CustomerResponse]:
        rows = self._repo.search(query.strip())
        return [self._to_response(r) for r in rows]
