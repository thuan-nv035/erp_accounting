from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class SalesReturnItemCreate(BaseModel):
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal = Decimal("0")


class SalesReturnCreate(BaseModel):
    return_no: str
    return_date: date

    sales_invoice_id: int | None = None
    customer_id: int

    description: str | None = None

    receivable_account_id: int
    sales_return_account_id: int
    tax_account_id: int | None = None

    items: list[SalesReturnItemCreate]


class SalesReturnItemResponse(BaseModel):
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


class SalesReturnResponse(BaseModel):
    id: int
    return_no: str
    return_date: date

    sales_invoice_id: int | None
    customer_id: int

    description: str | None

    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal

    receivable_account_id: int
    sales_return_account_id: int
    tax_account_id: int | None

    journal_entry_id: int | None

    items: list[SalesReturnItemResponse]

    model_config = {
        "from_attributes": True
    }