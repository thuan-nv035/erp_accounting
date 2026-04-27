from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class JournalLineCreate(BaseModel):
    account_id: int
    debit: Decimal = Decimal("0.00")
    credit: Decimal = Decimal("0.00")


class JournalEntryCreate(BaseModel):
    entry_date: date
    description: str
    lines: list[JournalLineCreate]


class JournalLineResponse(BaseModel):
    id: int
    account_id: int
    debit: Decimal
    credit: Decimal

    model_config = {
        "from_attributes": True
    }


class JournalEntryResponse(BaseModel):
    id: int
    entry_date: date
    description: str
    status: str
    lines: list[JournalLineResponse]

    model_config = {
        "from_attributes": True
    }