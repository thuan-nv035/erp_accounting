from datetime import date
from decimal import Decimal
from sqlalchemy import String, Date, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    entry_date: Mapped[date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="posted")

    lines: Mapped[list["JournalEntryLine"]] = relationship(
        back_populates="journal_entry",
        cascade="all, delete-orphan"
    )


class JournalEntryLine(Base):
    __tablename__ = "journal_entry_lines"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    journal_entry_id: Mapped[int] = mapped_column(
        ForeignKey("journal_entries.id")
    )

    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id")
    )

    debit: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0
    )

    credit: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0
    )

    journal_entry: Mapped["JournalEntry"] = relationship(
        back_populates="lines"
    )