from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db

from models.account import Account
from models.product import Product
from models.journal import JournalEntry, JournalEntryLine
from models.stock_adjustment import StockAdjustment, StockAdjustmentItem

from schemas.stock_adjustment import (
    StockAdjustmentCreate,
    StockAdjustmentResponse
)


router = APIRouter(
    prefix="/api/v1/stock-adjustments",
    tags=["Stock Adjustments"]
)


@router.post("/", response_model=StockAdjustmentResponse)
def create_stock_adjustment(
    data: StockAdjustmentCreate,
    db: Session = Depends(get_db)
):
    existed = db.query(StockAdjustment).filter(
        StockAdjustment.adjustment_no == data.adjustment_no
    ).first()

    if existed:
        raise HTTPException(
            status_code=400,
            detail="Số phiếu điều chỉnh kho đã tồn tại"
        )

    if not data.items:
        raise HTTPException(
            status_code=400,
            detail="Phiếu điều chỉnh phải có ít nhất 1 sản phẩm"
        )

    inventory_account = db.query(Account).filter(
        Account.id == data.inventory_account_id
    ).first()

    if not inventory_account:
        raise HTTPException(
            status_code=404,
            detail="Tài khoản hàng tồn kho không tồn tại"
        )

    adjustment_account = db.query(Account).filter(
        Account.id == data.adjustment_account_id
    ).first()

    if not adjustment_account:
        raise HTTPException(
            status_code=404,
            detail="Tài khoản điều chỉnh không tồn tại"
        )

    total_value = Decimal("0")
    adjustment_items = []

    for item in data.items:
        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Sản phẩm id={item.product_id} không tồn tại"
            )

        if item.quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail="Số lượng điều chỉnh phải lớn hơn 0"
            )

        if item.unit_cost < 0:
            raise HTTPException(
                status_code=400,
                detail="Đơn giá không được âm"
            )

        line_value = item.quantity * item.unit_cost
        total_value += line_value

        adjustment_items.append(
            StockAdjustmentItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_cost=item.unit_cost,
                line_value=line_value
            )
        )

    journal = JournalEntry(
        entry_date=data.adjustment_date,
        description=data.description or f"Điều chỉnh tồn kho {data.adjustment_no}",
        status="posted"
    )

    if data.adjustment_type == "increase":
        # Tăng kho:
        # Nợ 156
        # Có 711
        journal.lines.append(
            JournalEntryLine(
                account_id=data.inventory_account_id,
                debit=total_value,
                credit=Decimal("0")
            )
        )

        journal.lines.append(
            JournalEntryLine(
                account_id=data.adjustment_account_id,
                debit=Decimal("0"),
                credit=total_value
            )
        )

    elif data.adjustment_type == "decrease":
        # Giảm kho:
        # Nợ 811
        # Có 156
        journal.lines.append(
            JournalEntryLine(
                account_id=data.adjustment_account_id,
                debit=total_value,
                credit=Decimal("0")
            )
        )

        journal.lines.append(
            JournalEntryLine(
                account_id=data.inventory_account_id,
                debit=Decimal("0"),
                credit=total_value
            )
        )

    else:
        raise HTTPException(
            status_code=400,
            detail="Loại điều chỉnh không hợp lệ"
        )

    db.add(journal)
    db.flush()

    adjustment = StockAdjustment(
        adjustment_no=data.adjustment_no,
        adjustment_date=data.adjustment_date,
        adjustment_type=data.adjustment_type,
        description=data.description,
        inventory_account_id=data.inventory_account_id,
        adjustment_account_id=data.adjustment_account_id,
        total_value=total_value,
        journal_entry_id=journal.id
    )

    for adjustment_item in adjustment_items:
        adjustment.items.append(adjustment_item)

    db.add(adjustment)
    db.commit()
    db.refresh(adjustment)

    return adjustment


@router.get("/", response_model=list[StockAdjustmentResponse])
def get_stock_adjustments(
    db: Session = Depends(get_db)
):
    return (
        db.query(StockAdjustment)
        .order_by(StockAdjustment.id.desc())
        .all()
    )


@router.get("/{adjustment_id}", response_model=StockAdjustmentResponse)
def get_stock_adjustment(
    adjustment_id: int,
    db: Session = Depends(get_db)
):
    adjustment = db.query(StockAdjustment).filter(
        StockAdjustment.id == adjustment_id
    ).first()

    if not adjustment:
        raise HTTPException(
            status_code=404,
            detail="Phiếu điều chỉnh kho không tồn tại"
        )

    return adjustment