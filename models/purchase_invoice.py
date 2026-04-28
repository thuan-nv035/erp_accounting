from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class PurchaseInvoice(Base):
    __tablename__ = "purchase_invoices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    invoice_no: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True
    )

    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id")
    )

    invoice_date: Mapped[date] = mapped_column(Date)

    due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0
    )

    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0
    )

    purchase_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id")
    )

    tax_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts.id"),
        nullable=True
    )

    payable_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id")
    )

    journal_entry_id: Mapped[int | None] = mapped_column(
        ForeignKey("journal_entries.id"),
        nullable=True
    )

    items: Mapped[list["PurchaseInvoiceItem"]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan"
    )


class PurchaseInvoiceItem(Base):
    __tablename__ = "purchase_invoice_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("purchase_invoices.id")
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 2)
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(18, 2)
    )

    tax_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=0
    )

    line_subtotal: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0
    )

    line_tax: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0
    )

    line_total: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0
    )

    invoice: Mapped["PurchaseInvoice"] = relationship(
        back_populates="items"
    )