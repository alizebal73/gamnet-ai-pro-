import sqlite3
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException

from gamenet.server.db import utc_now_iso
from gamenet.server.models.credit import CreditGrantRequest
from gamenet.server.models.sale import PaymentConfirmRequest, PaymentResolutionRequest, RefundRequest, SaleCreateRequest, SaleResponse
from gamenet.server.services.credit_service import CreditService
from gamenet.server.services.audit_service import AuditService
from gamenet.server.services.balance_service import BalanceService
from gamenet.server.services.idempotency import claim_request
from gamenet.server.services.pricing_service import PricingService


class SaleService:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    @staticmethod
    def _response(row: sqlite3.Row) -> SaleResponse:
        return SaleResponse(
            id=row["id"], customer_id=row["customer_id"], item_type=row["item_type"],
            item_name=row["item_name"], duration_seconds=row["duration_seconds"], amount=row["amount"],
            status=row["sale_status"], payment_id=row["payment_id"], payment_status=row["payment_status"],
            price_snapshot=row["price_snapshot"], pricing_rule_id=row["pricing_rule_id"],
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
        quote = None
        amount = payload.amount
        package_id = payload.package_id
        vip_plan_id = payload.vip_plan_id
        item_name = payload.item_name
        duration_seconds = payload.duration_seconds
        if payload.item_type == "PACKAGE":
            package = self._conn.execute("SELECT * FROM packages WHERE id = ? AND active = 1", (package_id,)).fetchone()
            if not package:
                raise HTTPException(status_code=404, detail="Active package not found")
            amount = package["price"]
            item_name = package["name"]
            duration_seconds = package["duration_seconds"] + package["bonus_seconds"]
        if payload.item_type == "VIP":
            vip_plan = self._conn.execute("SELECT * FROM vip_plans WHERE id = ? AND active = 1", (vip_plan_id,)).fetchone()
            if not vip_plan:
                raise HTTPException(status_code=404, detail="Active VIP plan not found")
            amount = vip_plan["price"]
            item_name = vip_plan["name"]
            duration_seconds = 0
        if amount is None:
            quote = PricingService(self._conn).quote(payload.item_type, payload.duration_seconds)
            amount = quote.amount
        elif payload.item_type == "GAMING":
            quote = PricingService(self._conn).quote(payload.item_type, payload.duration_seconds)
            if amount != quote.amount:
                raise HTTPException(status_code=409, detail="Amount does not match the active pricing rule")
        now = utc_now_iso()
        sale_id = f"SALE-{uuid.uuid4().hex[:12].upper()}"
        payment_id = f"PAY-{uuid.uuid4().hex[:12].upper()}"
        self._conn.execute(
            "INSERT INTO sales (id, customer_id, operator_id, item_type, item_name, duration_seconds, amount, status, request_id, created_at, updated_at, pricing_rule_id, price_snapshot, package_id, vip_plan_id) VALUES (?, ?, ?, ?, ?, ?, ?, 'CREATED', ?, ?, ?, ?, ?, ?, ?)",
            (sale_id, payload.customer_id, operator_id, payload.item_type, item_name, duration_seconds, amount, payload.request_id, now, now, quote.pricing_rule_id if quote else None, amount, package_id, vip_plan_id),
        )
        self._conn.execute(
            "INSERT INTO payments (id, sale_id, method, amount, status, request_id, created_at, updated_at) VALUES (?, ?, ?, ?, 'PENDING', ?, ?, ?)",
            (payment_id, sale_id, payload.payment_method, amount, f"PAYMENT-{payload.request_id}", now, now),
        )
        AuditService.record(
            self._conn, action="SALE_CREATED", entity_type="SALE", entity_id=sale_id,
            request_id=payload.request_id, user_id=operator_id, customer_id=payload.customer_id,
            amount=amount, new_value={"item_type": payload.item_type, "payment_method": payload.payment_method},
        )
        return self._response(self._conn.execute("SELECT s.*, p.id AS payment_id, p.status AS payment_status, s.status AS sale_status FROM sales s JOIN payments p ON p.sale_id = s.id WHERE s.id = ?", (sale_id,)).fetchone())

    def confirm(self, sale_id: str, payload: PaymentConfirmRequest) -> SaleResponse:
        row = self._conn.execute(
            "SELECT s.*, p.id AS payment_id, p.method AS payment_method, p.status AS payment_status, s.status AS sale_status FROM sales s JOIN payments p ON p.sale_id = s.id WHERE s.id = ?", (sale_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Sale not found")
        if row["payment_status"] == "PAID":
            return self._response(row)
        if row["payment_status"] not in ("PENDING", "PROCESSING"):
            raise HTTPException(status_code=409, detail="Payment cannot be confirmed from current state")
        if not claim_request(
            self._conn, request_id=payload.request_id, operation="PAYMENT_CONFIRM",
            entity_type="SALE", entity_id=sale_id,
        ):
            return self._response(row)
        now = utc_now_iso()
        if row["payment_method"] == "BALANCE":
            BalanceService(self._conn).apply(
                customer_id=row["customer_id"], delta_amount=-row["amount"], event_type="PURCHASE",
                request_id=f"BALANCE-{sale_id}", sale_id=sale_id,
                reason=f"Payment for sale {sale_id}", actor_id=row["operator_id"],
            )
        self._conn.execute("UPDATE payments SET status = 'PAID', reference = ?, updated_at = ? WHERE id = ?", (payload.reference, now, row["payment_id"]))
        self._conn.execute("UPDATE sales SET status = 'PAID', updated_at = ? WHERE id = ?", (now, sale_id))
        if row["item_type"] in ("GAMING", "PACKAGE") and row["duration_seconds"] > 0:
            expires_at = None
            if row["package_id"]:
                package = self._conn.execute("SELECT expiry_days FROM packages WHERE id = ?", (row["package_id"],)).fetchone()
                if package and package["expiry_days"]:
                    expires_at = (datetime.now(UTC) + timedelta(days=package["expiry_days"])).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            CreditService(self._conn).grant(
                row["customer_id"],
                CreditGrantRequest(
                    credit_type="PACKAGE" if row["item_type"] == "PACKAGE" else "PAID",
                    seconds=row["duration_seconds"], source=sale_id,
                    reason=f"Paid sale {sale_id}", request_id=f"CREDIT-{sale_id}", expires_at=expires_at,
                ),
            )
        if row["item_type"] == "RECHARGE":
            BalanceService(self._conn).apply(
                customer_id=row["customer_id"], delta_amount=row["amount"], event_type="RECHARGE",
                request_id=f"RECHARGE-{sale_id}", sale_id=sale_id,
                reason=f"Recharge from sale {sale_id}", actor_id=row["operator_id"],
            )
        if row["item_type"] == "VIP" and row["vip_plan_id"]:
            plan = self._conn.execute("SELECT duration_days FROM vip_plans WHERE id = ?", (row["vip_plan_id"],)).fetchone()
            starts_at = datetime.now(UTC).replace(microsecond=0)
            expires_at = (starts_at + timedelta(days=plan["duration_days"])).isoformat().replace("+00:00", "Z")
            self._conn.execute(
                "INSERT INTO customer_vip (id, customer_id, plan_id, sale_id, starts_at, expires_at, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (f"CUSTOMER-VIP-{uuid.uuid4().hex[:12].upper()}", row["customer_id"], row["vip_plan_id"], sale_id, starts_at.isoformat().replace("+00:00", "Z"), expires_at, now),
            )
        AuditService.record(
            self._conn, action="PAYMENT_CONFIRMED", entity_type="PAYMENT", entity_id=row["payment_id"],
            request_id=payload.request_id, user_id=row["operator_id"], customer_id=row["customer_id"],
            amount=row["amount"], new_value={"status": "PAID", "reference": payload.reference},
        )
        return self._response(self._conn.execute("SELECT s.*, p.id AS payment_id, p.status AS payment_status, s.status AS sale_status FROM sales s JOIN payments p ON p.sale_id = s.id WHERE s.id = ?", (sale_id,)).fetchone())

    def mark_unknown(self, sale_id: str, payload: PaymentConfirmRequest) -> SaleResponse:
        row = self._conn.execute("SELECT s.*, p.id AS payment_id, p.status AS payment_status, s.status AS sale_status FROM sales s JOIN payments p ON p.sale_id = s.id WHERE s.id = ?", (sale_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Sale not found")
        if row["payment_status"] == "UNKNOWN":
            return self._response(row)
        if row["payment_status"] not in ("PENDING", "PROCESSING"):
            raise HTTPException(status_code=409, detail="Payment cannot become UNKNOWN from current state")
        if not claim_request(
            self._conn, request_id=payload.request_id, operation="PAYMENT_UNKNOWN",
            entity_type="SALE", entity_id=sale_id,
        ):
            return self._response(row)
        self._conn.execute("UPDATE payments SET status = 'UNKNOWN', reference = ?, updated_at = ? WHERE id = ?", (payload.reference, utc_now_iso(), row["payment_id"]))
        AuditService.record(
            self._conn, action="PAYMENT_UNKNOWN", entity_type="PAYMENT", entity_id=row["payment_id"],
            request_id=payload.request_id, user_id=row["operator_id"], customer_id=row["customer_id"],
            amount=row["amount"], new_value={"status": "UNKNOWN", "reference": payload.reference},
        )
        return self._response(self._conn.execute("SELECT s.*, p.id AS payment_id, p.status AS payment_status, s.status AS sale_status FROM sales s JOIN payments p ON p.sale_id = s.id WHERE s.id = ?", (sale_id,)).fetchone())

    def resolve(self, sale_id: str, payload: PaymentResolutionRequest) -> SaleResponse:
        row = self._conn.execute("SELECT * FROM payments WHERE sale_id = ?", (sale_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Sale not found")
        if row["status"] != "UNKNOWN":
            raise HTTPException(status_code=409, detail="Only UNKNOWN payments require resolution")
        if payload.status == "FAILED":
            self._conn.execute("UPDATE payments SET status = 'FAILED', reference = ?, updated_at = ? WHERE id = ?", (payload.reference, utc_now_iso(), row["id"]))
            return self._response(self._conn.execute("SELECT s.*, p.id AS payment_id, p.status AS payment_status, s.status AS sale_status FROM sales s JOIN payments p ON p.sale_id = s.id WHERE s.id = ?", (sale_id,)).fetchone())
        self._conn.execute("UPDATE payments SET status = 'PENDING', updated_at = ? WHERE id = ?", (utc_now_iso(), row["id"]))
        return self.confirm(sale_id, PaymentConfirmRequest(reference=payload.reference, request_id=payload.request_id))

    def request_refund(self, sale_id: str, payload: RefundRequest, actor_id: str) -> SaleResponse:
        row = self._conn.execute("SELECT s.*, p.id AS payment_id, p.status AS payment_status, s.status AS sale_status FROM sales s JOIN payments p ON p.sale_id = s.id WHERE s.id = ?", (sale_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Sale not found")
        if row["payment_status"] == "REFUND_PENDING":
            return self._response(row)
        if row["payment_status"] != "PAID":
            raise HTTPException(status_code=409, detail="Only PAID payments can be refunded")
        if not claim_request(
            self._conn, request_id=payload.request_id, operation="REFUND_REQUEST",
            entity_type="SALE", entity_id=sale_id,
        ):
            return self._response(row)
        now = utc_now_iso()
        self._conn.execute("UPDATE payments SET status = 'REFUND_PENDING', reference = ?, updated_at = ? WHERE id = ?", (payload.reason, now, row["payment_id"]))
        self._conn.execute("UPDATE sales SET status = 'REFUND_PENDING', updated_at = ? WHERE id = ?", (now, sale_id))
        AuditService.record(
            self._conn, action="REFUND_REQUESTED", entity_type="SALE", entity_id=sale_id,
            request_id=payload.request_id, user_id=actor_id, customer_id=row["customer_id"], amount=row["amount"],
            reason=payload.reason, new_value={"status": "REFUND_PENDING"},
        )
        return self._response(self._conn.execute("SELECT s.*, p.id AS payment_id, p.status AS payment_status, s.status AS sale_status FROM sales s JOIN payments p ON p.sale_id = s.id WHERE s.id = ?", (sale_id,)).fetchone())

    def approve_refund(self, sale_id: str, payload: RefundRequest, actor_id: str) -> SaleResponse:
        row = self._conn.execute("SELECT s.*, p.id AS payment_id, p.status AS payment_status, s.status AS sale_status FROM sales s JOIN payments p ON p.sale_id = s.id WHERE s.id = ?", (sale_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Sale not found")
        if row["payment_status"] == "REFUNDED":
            return self._response(row)
        if row["payment_status"] != "REFUND_PENDING":
            raise HTTPException(status_code=409, detail="Refund approval is not pending")
        if not claim_request(
            self._conn, request_id=payload.request_id, operation="REFUND_APPROVE",
            entity_type="SALE", entity_id=sale_id,
        ):
            return self._response(row)
        entitlement = self._conn.execute("SELECT * FROM entitlements WHERE source = ?", (sale_id,)).fetchone()
        if entitlement and entitlement["consumed_seconds"] > 0:
            raise HTTPException(status_code=409, detail="Consumed credit cannot be automatically refunded")
        now = utc_now_iso()
        if entitlement:
            self._conn.execute("UPDATE entitlements SET status = 'CANCELLED', updated_at = ? WHERE id = ?", (now, entitlement["id"]))
            self._conn.execute("INSERT INTO entitlement_ledger (id, entitlement_id, customer_id, delta_seconds, event_type, request_id, reason, created_at) VALUES (?, ?, ?, ?, 'REFUND', ?, ?, ?)", (f"LEDGER-{uuid.uuid4().hex[:12].upper()}", entitlement["id"], entitlement["customer_id"], -entitlement["granted_seconds"], f"REFUND-{sale_id}", payload.reason, now))
        self._conn.execute("UPDATE payments SET status = 'REFUNDED', updated_at = ? WHERE id = ?", (now, row["payment_id"]))
        self._conn.execute("UPDATE sales SET status = 'REFUNDED', updated_at = ? WHERE id = ?", (now, sale_id))
        AuditService.record(
            self._conn, action="REFUND_APPROVED", entity_type="SALE", entity_id=sale_id,
            request_id=payload.request_id, user_id=actor_id, customer_id=row["customer_id"], amount=row["amount"],
            reason=payload.reason, new_value={"status": "REFUNDED"},
        )
        return self._response(self._conn.execute("SELECT s.*, p.id AS payment_id, p.status AS payment_status, s.status AS sale_status FROM sales s JOIN payments p ON p.sale_id = s.id WHERE s.id = ?", (sale_id,)).fetchone())