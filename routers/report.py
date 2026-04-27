from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.account import Account
from models.journal import JournalEntryLine
from schemas.report import TrialBalanceResponse, TrialBalanceItem

router = APIRouter(
    prefix="/api/v1/reports",
    tags=["Reports"]
)


@router.get("/trial-balance", response_model=TrialBalanceResponse)
def get_trial_balance(db: Session = Depends(get_db)):
    accounts = db.query(Account).order_by(Account.code.asc()).all()

    items = []

    total_debit_all = Decimal("0.00")
    total_credit_all = Decimal("0.00")
    total_debit_balance = Decimal("0.00")
    total_credit_balance = Decimal("0.00")

    for account in accounts:
        lines = db.query(JournalEntryLine).filter(
            JournalEntryLine.account_id == account.id
        ).all()

        total_debit = sum(
            (line.debit or Decimal("0.00")) for line in lines
        )

        total_credit = sum(
            (line.credit or Decimal("0.00")) for line in lines
        )

        balance = total_debit - total_credit

        if balance >= 0:
            debit_balance = balance
            credit_balance = Decimal("0.00")
        else:
            debit_balance = Decimal("0.00")
            credit_balance = abs(balance)

        total_debit_all += total_debit
        total_credit_all += total_credit
        total_debit_balance += debit_balance
        total_credit_balance += credit_balance

        items.append(
            TrialBalanceItem(
                account_id=account.id,
                account_code=account.code,
                account_name=account.name,
                account_type=account.type,
                total_debit=total_debit,
                total_credit=total_credit,
                debit_balance=debit_balance,
                credit_balance=credit_balance
            )
        )

    return TrialBalanceResponse(
        total_debit=total_debit_all,
        total_credit=total_credit_all,
        total_debit_balance=total_debit_balance,
        total_credit_balance=total_credit_balance,
        is_balanced=total_debit_all == total_credit_all,
        items=items
    )