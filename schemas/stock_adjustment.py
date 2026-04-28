from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


class StockAdjustmentItemCreate(BaseModel):
    product_id: int
    quantity: Decimal
    unit_cost: Decimal


class StockAdjustmentCreate(BaseModel):
    adjustment_no: str
    adjustment_date: date

    adjustment_type: Literal["increase", "decrease"]

    description: str | None = None

    inventory_account_id: int
    adjustment_account_id: int

    items: list[StockAdjustmentItemCreate]


class StockAdjustmentItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    unit_cost: Decimal
    line_value: Decimal

    model_config = {
        "from_attributes": True
    }


class StockAdjustmentResponse(BaseModel):
    id: int
    adjustment_no: str
    adjustment_date: date
    adjustment_type: str
    description: str | None

    inventory_account_id: int
    adjustment_account_id: int

    total_value: Decimal
    journal_entry_id: int | None

    items: list[StockAdjustmentItemResponse]

    model_config = {
        "from_attributes": True
    }