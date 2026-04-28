from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class SalesReturn(Base):
    __tablename__ = "sales_returns"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    return_no: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True
    )

    return_date: Mapped[date] = mapped_column(Date)

    sales_invoice_id: Mapped[int | None] = mapped_column(
        ForeignKey("sales_invoices.id"),
        nullable=True
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id")
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

    receivable_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id")
    )

    sales_return_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id")
    )

    tax_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts.id"),
        nullable=True
    )

    journal_entry_id: Mapped[int | None] = mapped_column(
        ForeignKey("journal_entries.id"),
        nullable=True
    )

    items: Mapped[list["SalesReturnItem"]] = relationship(
        back_populates="sales_return",
        cascade="all, delete-orphan"
    )


class SalesReturnItem(Base):
    __tablename__ = "sales_return_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    sales_return_id: Mapped[int] = mapped_column(
        ForeignKey("sales_returns.id")
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

    sales_return: Mapped["SalesReturn"] = relationship(
        back_populates="items"
    )