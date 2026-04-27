from decimal import Decimal
from sqlalchemy import String, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    unit: Mapped[str] = mapped_column(String(50), default="cái")

    cost_price: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    sale_price: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)