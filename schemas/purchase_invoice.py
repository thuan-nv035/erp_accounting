from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class PurchaseInvoiceItemCreate(BaseModel):
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal = Decimal("0")


class PurchaseInvoiceCreate(BaseModel):
    invoice_no: str
    supplier_id: int

    invoice_date: date
    due_date: date | None = None

    description: str | None = None

    purchase_account_id: int
    tax_account_id: int | None = None
    payable_account_id: int

    items: list[PurchaseInvoiceItemCreate]


class PurchaseInvoiceItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal
    line_subtotal: Decimal
    line_tax: Decimal
    line_total: Decimal

    model_config = {
        "from_attributes": True
    }


class PurchaseInvoiceResponse(BaseModel):
    id: int
    invoice_no: str
    supplier_id: int

    invoice_date: date
    due_date: date | None

    description: str | None

    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal

    purchase_account_id: int
    tax_account_id: int | None
    payable_account_id: int

    journal_entry_id: int | None

    items: list[PurchaseInvoiceItemResponse]

    model_config = {
        "from_attributes": True
    }