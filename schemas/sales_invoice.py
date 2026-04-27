from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class SalesInvoiceItemCreate(BaseModel):
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    vat_rate: Decimal = Decimal("0.00")


class SalesInvoiceCreate(BaseModel):
    invoice_no: str
    customer_id: int
    invoice_date: date
    due_date: date | None = None
    description: str | None = None

    receivable_account_id: int
    revenue_account_id: int
    tax_account_id: int | None = None

    items: list[SalesInvoiceItemCreate]


class SalesInvoiceItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    vat_rate: Decimal
    line_subtotal: Decimal
    line_vat: Decimal
    line_total: Decimal

    model_config = {
        "from_attributes": True
    }


class SalesInvoiceResponse(BaseModel):
    id: int
    invoice_no: str
    customer_id: int
    journal_entry_id: int | None
    invoice_date: date
    due_date: date | None
    description: str | None
    status: str
    subtotal: Decimal
    vat_amount: Decimal
    total_amount: Decimal
    items: list[SalesInvoiceItemResponse]

    model_config = {
        "from_attributes": True
    }