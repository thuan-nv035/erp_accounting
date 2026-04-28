from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class ReceivePaymentCreate(BaseModel):
    payment_no: str
    payment_date: date

    invoice_id: int | None = None
    customer_id: int

    cash_account_id: int
    receivable_account_id: int

    amount: Decimal
    payment_method: str = "cash"
    description: str | None = None


class PaymentResponse(BaseModel):
    id: int
    payment_no: str
    payment_date: date

    invoice_id: int | None
    customer_id: int

    cash_account_id: int
    receivable_account_id: int

    amount: Decimal
    payment_method: str
    description: str | None
    journal_entry_id: int | None

    model_config = {
        "from_attributes": True
    }

class PaySupplierCreate(BaseModel):
    payment_no: str
    payment_date: date

    purchase_invoice_id: int | None = None
    supplier_id: int

    cash_account_id: int
    payable_account_id: int

    amount: Decimal
    payment_method: str = "cash"
    description: str | None = None


class SupplierPaymentResponse(BaseModel):
    id: int
    payment_no: str
    payment_date: date

    purchase_invoice_id: int | None
    supplier_id: int

    cash_account_id: int
    payable_account_id: int

    amount: Decimal
    payment_method: str
    description: str | None
    journal_entry_id: int | None

    model_config = {
        "from_attributes": True
    }