import sqlite3
import uuid

from fastapi import HTTPException

from gamenet.server.db import utc_now_iso
from gamenet.server.models.credit import CreditGrantRequest
from gamenet.server.models.sale import PaymentConfirmRequest, SaleCreateRequest, SaleResponse
from gamenet.server.services.credit_service import CreditService


class SaleService:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    @staticmethod
    def _response(row: sqlite3.Row) -> SaleResponse:
        return SaleResponse(
            id=row["id"], customer_id=row["customer_id"], item_type=row["item_type"],
            item_name=row["item_name"], duration_seconds=row["duration_seconds"], amount=row["amount"],
            status=row["sale_status"], payment_id=row["payment_id"], payment_status=row["payment_status"],
        )

    def create(self, payload: SaleCreateRequest, operator_id: str) -> SaleResponse:
        existing = self._conn.execute(
            """
            SELECT s.*, p.id AS payment_id, p.status AS payment_status, s.status AS sale_status
            FROM sales s JOIN payments p ON p.sale_id = s.id WHERE s.request_id = ?
            """, (payload.request_id,)
        ).fetchone()
        if existing:
            return self._response(existing)
        customer = self._conn.execute("SELECT id FROM customers WHERE id = ? AND status = 'ACTIVE'", (payload.customer_id,)).fetchone()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        now = utc_now_iso()
        sale_id = f"SALE-{uuid.uuid4().hex[:12].upper()}"
        payment_id = f"PAY-{uuid.uuid4().hex[:12].upper()}"
        self._conn.execute(
            "INSERT INTO sales (id, customer_id, operator_id, item_type, item_name, duration_seconds, amount, status, request_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, 'CREATED', ?, ?, ?)",
            (sale_id, payload.customer_id, operator_id, payload.item_type, payload.item_name, payload.duration_seconds, payload.amount, payload.request_id, now, now),
        )
        self._conn.execute(
            "INSERT INTO payments (id, sale_id, method, amount, status, request_id, created_at, updated_at) VALUES (?, ?, ?, ?, 'PENDING', ?, ?, ?)",
            (payment_id, sale_id, payload.payment_method, payload.amount, f"PAYMENT-{payload.request_id}", now, now),
        )
        return self._response(self._conn.execute("SELECT s.*, p.id AS payment_id, p.status AS payment_status, s.status AS sale_status FROM sales s JOIN payments p ON p.sale_id = s.id WHERE s.id = ?", (sale_id,)).fetchone())

    def confirm(self, sale_id: str, payload: PaymentConfirmRequest) -> SaleResponse:
        row = self._conn.execute(
            "SELECT s.*, p.id AS payment_id, p.status AS payment_status, s.status AS sale_status FROM sales s JOIN payments p ON p.sale_id = s.id WHERE s.id = ?", (sale_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Sale not found")
        if row["payment_status"] == "PAID":
            return self._response(row)
        if row["payment_status"] not in ("PENDING", "PROCESSING"):
            raise HTTPException(status_code=409, detail="Payment cannot be confirmed from current state")
        now = utc_now_iso()
        self._conn.execute("UPDATE payments SET status = 'PAID', reference = ?, updated_at = ? WHERE id = ?", (payload.reference, now, row["payment_id"]))
        self._conn.execute("UPDATE sales SET status = 'PAID', updated_at = ? WHERE id = ?", (now, sale_id))
        if row["item_type"] in ("GAMING", "PACKAGE") and row["duration_seconds"] > 0:
            CreditService(self._conn).grant(
                row["customer_id"],
                CreditGrantRequest(
                    credit_type="PACKAGE" if row["item_type"] == "PACKAGE" else "PAID",
                    seconds=row["duration_seconds"], source=sale_id,
                    reason=f"Paid sale {sale_id}", request_id=f"CREDIT-{sale_id}",
                ),
            )
        return self._response(self._conn.execute("SELECT s.*, p.id AS payment_id, p.status AS payment_status, s.status AS sale_status FROM sales s JOIN payments p ON p.sale_id = s.id WHERE s.id = ?", (sale_id,)).fetchone())