import uuid

from fastapi import APIRouter, Depends, HTTPException

from gamenet.server.db import get_connection, utc_now_iso
from gamenet.server.models.inventory import InventoryAdjustRequest, InventoryCreateRequest, InventoryResponse
from gamenet.server.security.auth import require_permission
from gamenet.server.services.audit_service import AuditService

router = APIRouter(prefix="/inventory", tags=["inventory"])


def _response(row) -> InventoryResponse:
    return InventoryResponse(id=row["id"], name=row["name"], sku=row["sku"], sale_price=row["sale_price"], stock=row["stock"], minimum_stock=row["minimum_stock"])


@router.get("", response_model=list[InventoryResponse])
def list_inventory(_user: dict = Depends(require_permission("inventory.view"))) -> list[InventoryResponse]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM inventory_items WHERE active = 1 ORDER BY name").fetchall()
    return [_response(row) for row in rows]


@router.post("", response_model=InventoryResponse, status_code=201)
def create_inventory(payload: InventoryCreateRequest, user: dict = Depends(require_permission("inventory.manage"))) -> InventoryResponse:
    item_id = f"ITEM-{uuid.uuid4().hex[:12].upper()}"
    now = utc_now_iso()
    with get_connection() as conn:
        conn.execute("INSERT INTO inventory_items (id, name, sku, purchase_price, sale_price, stock, minimum_stock, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (item_id, payload.name, payload.sku, payload.purchase_price, payload.sale_price, payload.initial_stock, payload.minimum_stock, now, now))
        if payload.initial_stock:
            conn.execute("INSERT INTO inventory_transactions (id, item_id, delta_stock, event_type, request_id, reason, created_at) VALUES (?, ?, ?, 'MANUAL_ADJUSTMENT', ?, ?, ?)", (f"INV-TX-{uuid.uuid4().hex[:12].upper()}", item_id, payload.initial_stock, f"INITIAL-{item_id}", "Initial stock", now))
        AuditService.record(conn, action="INVENTORY_CREATED", entity_type="INVENTORY_ITEM", entity_id=item_id, user_id=user["id"], new_value=payload.model_dump())
        return _response(conn.execute("SELECT * FROM inventory_items WHERE id = ?", (item_id,)).fetchone())


@router.post("/{item_id}/adjust", response_model=InventoryResponse)
def adjust_inventory(item_id: str, payload: InventoryAdjustRequest, user: dict = Depends(require_permission("inventory.manage"))) -> InventoryResponse:
    now = utc_now_iso()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM inventory_items WHERE id = ? AND active = 1", (item_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        if row["stock"] + payload.delta_stock < 0:
            raise HTTPException(status_code=409, detail="Insufficient inventory stock")
        conn.execute("UPDATE inventory_items SET stock = stock + ?, updated_at = ? WHERE id = ?", (payload.delta_stock, now, item_id))
        conn.execute("INSERT INTO inventory_transactions (id, item_id, delta_stock, event_type, request_id, reason, created_at) VALUES (?, ?, ?, 'MANUAL_ADJUSTMENT', ?, ?, ?)", (f"INV-TX-{uuid.uuid4().hex[:12].upper()}", item_id, payload.delta_stock, payload.request_id, payload.reason, now))
        AuditService.record(conn, action="INVENTORY_ADJUSTED", entity_type="INVENTORY_ITEM", entity_id=item_id, user_id=user["id"], request_id=payload.request_id, amount=payload.delta_stock, reason=payload.reason)
        return _response(conn.execute("SELECT * FROM inventory_items WHERE id = ?", (item_id,)).fetchone())