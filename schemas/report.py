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