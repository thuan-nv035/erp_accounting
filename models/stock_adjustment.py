from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class StockAdjustment(Base):
    __tablename__ = "stock_adjustments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    adjustment_no: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True
    )

    adjustment_date: Mapped[date] = mapped_column(Date)

    adjustment_type: Mapped[str] = mapped_column(String(20))
    # increase hoặc decrease

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    inventory_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id")
    )

    adjustment_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id")
    )

    total_value: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0
    )

    journal_entry_id: Mapped[int | None] = mapped_column(
        ForeignKey("journal_entries.id"),
        nullable=True
    )

    items: Mapped[list["StockAdjustmentItem"]] = relationship(
        back_populates="adjustment",
        cascade="all, delete-orphan"
    )


class StockAdjustmentItem(Base):
    __tablename__ = "stock_adjustment_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    adjustment_id: Mapped[int] = mapped_column(
        ForeignKey("stock_adjustments.id")
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 2)
    )

    unit_cost: Mapped[Decimal] = mapped_column(
        Numeric(18, 2)
    )

    line_value: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0
    )

    adjustment: Mapped["StockAdjustment"] = relationship(
        back_populates="items"
    )