from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    payment_no: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    payment_date: Mapped[date] = mapped_column(Date)

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("sales_invoices.id"),
        nullable=True
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id")
    )

    cash_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id")
    )

    receivable_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id")
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0
    )

    payment_method: Mapped[str] = mapped_column(
        String(50),
        default="cash"
    )

    description: Mapped[str] = mapped_column(
        String(500),
        nullable=True
    )

    journal_entry_id: Mapped[int] = mapped_column(
        ForeignKey("journal_entries.id"),
        nullable=True
    )

class SupplierPayment(Base):
    __tablename__ = "supplier_payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    payment_no: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True
    )

    payment_date: Mapped[date] = mapped_column(Date)

    purchase_invoice_id: Mapped[int | None] = mapped_column(
        ForeignKey("purchase_invoices.id"),
        nullable=True
    )

    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id")
    )

    cash_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id")
    )

    payable_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id")
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0
    )

    payment_method: Mapped[str] = mapped_column(
        String(50),
        default="cash"
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    journal_entry_id: Mapped[int | None] = mapped_column(
        ForeignKey("journal_entries.id"),
        nullable=True
    )