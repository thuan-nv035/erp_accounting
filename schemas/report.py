from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class LedgerLineResponse(BaseModel):
    journal_entry_id: int
    entry_date: date
    description: str
    debit: Decimal
    credit: Decimal
    balance: Decimal


class LedgerResponse(BaseModel):
    account_id: int
    account_code: str
    account_name: str
    account_type: str
    total_debit: Decimal
    total_credit: Decimal
    ending_balance: Decimal
    lines: list[LedgerLineResponse]


class TrialBalanceItem(BaseModel):
    account_id: int
    account_code: str
    account_name: str
    account_type: str
    total_debit: Decimal
    total_credit: Decimal
    debit_balance: Decimal
    credit_balance: Decimal


class TrialBalanceResponse(BaseModel):
    total_debit: Decimal
    total_credit: Decimal
    total_debit_balance: Decimal
    total_credit_balance: Decimal
    is_balanced: bool
    items: list[TrialBalanceItem]

class ProfitLossLineResponse(BaseModel):
    account_id: int
    account_code: str
    account_name: str
    account_type: str
    amount: Decimal


class ProfitLossResponse(BaseModel):
    date_from: date | None = None
    date_to: date | None = None
    total_revenue: Decimal
    total_expense: Decimal
    net_profit: Decimal
    lines: list[ProfitLossLineResponse]

class BalanceSheetLineResponse(BaseModel):
    account_id: int
    account_code: str
    account_name: str
    account_type: str
    balance: Decimal


class BalanceSheetSectionResponse(BaseModel):
    total: Decimal
    lines: list[BalanceSheetLineResponse]


class BalanceSheetResponse(BaseModel):
    date_to: date | None = None

    total_assets: Decimal
    total_liabilities: Decimal
    total_equity: Decimal
    total_liabilities_and_equity: Decimal

    is_balanced: bool

    assets: BalanceSheetSectionResponse
    liabilities: BalanceSheetSectionResponse
    equity: BalanceSheetSectionResponse

class ReceivableLineResponse(BaseModel):
    invoice_id: int
    invoice_no: str
    customer_id: int
    invoice_date: date
    due_date: date | None
    total_amount: Decimal
    paid_amount: Decimal
    balance: Decimal
    status: str


class ReceivablesResponse(BaseModel):
    date_to: date | None = None
    total_invoiced: Decimal
    total_paid: Decimal
    total_balance: Decimal
    lines: list[ReceivableLineResponse]


class PayableLineResponse(BaseModel):
    invoice_id: int
    invoice_no: str
    supplier_id: int
    invoice_date: date
    due_date: date | None
    total_amount: Decimal
    paid_amount: Decimal
    balance: Decimal
    status: str


class PayablesResponse(BaseModel):
    date_to: date | None = None
    total_invoiced: Decimal
    total_paid: Decimal
    total_balance: Decimal
    lines: list[PayableLineResponse]

class InventoryLineResponse(BaseModel):
    product_id: int
    product_name: str
    purchased_qty: Decimal
    sold_qty: Decimal
    ending_qty: Decimal
    avg_purchase_price: Decimal
    inventory_value: Decimal


class InventoryReportResponse(BaseModel):
    total_inventory_value: Decimal
    lines: list[InventoryLineResponse]