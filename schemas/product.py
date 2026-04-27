from decimal import Decimal
from pydantic import BaseModel


class ProductCreate(BaseModel):
    sku: str
    name: str
    unit: str = "cái"
    cost_price: Decimal = Decimal("0.00")
    sale_price: Decimal = Decimal("0.00")


class ProductUpdate(BaseModel):
    name: str | None = None
    unit: str | None = None
    cost_price: Decimal | None = None
    sale_price: Decimal | None = None
    is_active: bool | None = None


class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    unit: str
    cost_price: Decimal
    sale_price: Decimal
    is_active: bool

    model_config = {
        "from_attributes": True
    }