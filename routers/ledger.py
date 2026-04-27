from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.account import Account
from models.journal import JournalEntry, JournalEntryLine
from schemas.report import LedgerResponse, LedgerLineResponse

router = APIRouter(
    prefix="/api/v1/ledger",
    tags=["Ledger"]
)


@router.get("/{account_id}", response_model=LedgerResponse)
def get_ledger(
    account_id: int,
    db: Session = Depends(get_db),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None)
):
    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        raise HTTPException(
            status_code=404,
            detail=f"Tài khoản id={account_id} không tồn tại"
        )

    query = (
        db.query(JournalEntryLine, JournalEntry)
        .join(
            JournalEntry,
            JournalEntryLine.journal_entry_id == JournalEntry.id
        )
        .filter(JournalEntryLine.account_id == account_id)
    )

    if date_from:
        query = query.filter(JournalEntry.entry_date >= date_from)

    if date_to:
        query = query.filter(JournalEntry.entry_date <= date_to)

    rows = query.order_by(
        JournalEntry.entry_date.asc(),
        JournalEntry.id.asc()
    ).all()

    total_debit = Decimal("0.00")
    total_credit = Decimal("0.00")
    running_balance = Decimal("0.00")

    lines = []

    for line, entry in rows:
        debit = line.debit or Decimal("0.00")
        credit = line.credit or Decimal("0.00")

        total_debit += debit
        total_credit += credit

        running_balance += debit - credit

        lines.append(
            LedgerLineResponse(
                journal_entry_id=entry.id,
                entry_date=entry.entry_date,
                description=entry.description,
                debit=debit,
                credit=credit,
                balance=running_balance
            )
        )

    ending_balance = total_debit - total_credit

    return LedgerResponse(
        account_id=account.id,
        account_code=account.code,
        account_name=account.name,
        account_type=account.type,
        total_debit=total_debit,
        total_credit=total_credit,
        ending_balance=ending_balance,
        lines=lines
    )