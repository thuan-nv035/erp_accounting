from decimal import Decimal
from http.client import HTTPException

from sqlalchemy.orm import Session

from models.journal import JournalEntryLine, JournalEntry
from schemas.journal import JournalEntryCreate


def create_journal_entry(db: Session, data: JournalEntryCreate):
    if len(data.lines) < 2:
        raise HTTPException(
            status_code = 400,
            detail = "Một bút kế toán phải có ít nhất 2 dòng"
        )

    total_debit = sum(line.debit for line in data.lines)
    total_credit = sum(line.credit for line in data.lines)

    if total_debit <= Decimal("0"):
        raise HTTPException(
            status_code = 400,
            detail="Tổng nợ phải lớn hơn 0"
        )

    if total_debit != total_credit:
        raise HTTPException(
            status_code=400,
            detail="Bút toán không cân. Tổng Nợ phải bằng Tổng Có"
        )

    for line in data.lines:
        if line.debit > 0 and line.credit > 0:
            raise HTTPException(
                status_code=400,
                detail="Một dòng không được vừa Nợ vừa Có"
            )

        if line.debit == 0 and line.credit == 0:
            raise HTTPException(
                status_code=400,
                detail="Một dòng phải có Nợ hoặc Có"
            )

    journal = JournalEntry(
        entry_date=data.entry_date,
        description=data.description,
        status="posted"
    )

    for line in data.lines:
        journal.lines.append(
            JournalEntryLine(
                account_id=line.account_id,
                debit=line.debit,
                credit=line.credit
            )
        )

    db.add(journal)
    db.commit()
    db.refresh(journal)

    return journal