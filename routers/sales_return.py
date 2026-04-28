from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db

from models.account import Account
from models.partner import Customer
from models.product import Product
from models.sales_invoice import SalesInvoice
from models.journal import JournalEntry, JournalEntryLine
from models.sales_return import SalesReturn, SalesReturnItem

from schemas.sales_return import (
    SalesReturnCreate,
    SalesReturnResponse
)


router = APIRouter(
    prefix="/api/v1/sales-returns",
    tags=["Sales Returns"]
)


@router.post("/", response_model=SalesReturnResponse)
def create_sales_return(
    data: SalesReturnCreate,
    db: Session = Depends(get_db)
):
    existed = db.query(SalesReturn).filter(
        SalesReturn.return_no == data.return_no
    ).first()

    if existed:
        raise HTTPException(
            status_code=400,
            detail="Số phiếu trả hàng bán đã tồn tại"
        )

    customer = db.query(Customer).filter(
        Customer.id == data.customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Khách hàng/đối tác không tồn tại"
        )

    if data.sales_invoice_id is not None:
        invoice = db.query(SalesInvoice).filter(
            SalesInvoice.id == data.sales_invoice_id
        ).first()

        if not invoice:
            raise HTTPException(
                status_code=404,
                detail="Hóa đơn bán hàng không tồn tại"
            )

    receivable_account = db.query(Account).filter(
        Account.id == data.receivable_account_id
    ).first()

    if not receivable_account:
        raise HTTPException(
            status_code=404,
            detail="Tài khoản phải thu không tồn tại"
        )

    sales_return_account = db.query(Account).filter(
        Account.id == data.sales_return_account_id
    ).first()

    if not sales_return_account:
        raise HTTPException(
            status_code=404,
            detail="Tài khoản hàng bán bị trả lại không tồn tại"
        )

    tax_account = None

    if data.tax_account_id is not None:
        tax_account = db.query(Account).filter(
            Account.id == data.tax_account_id
        ).first()

        if not tax_account:
            raise HTTPException(
                status_code=404,
                detail="Tài khoản thuế GTGT phải nộp không tồn tại"
            )

    if not data.items:
        raise HTTPException(
            status_code=400,
            detail="Phiếu trả hàng phải có ít nhất 1 sản phẩm"
        )

    subtotal = Decimal("0")
    tax_amount = Decimal("0")
    return_items = []

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
                detail="Số lượng trả phải lớn hơn 0"
            )

        if item.unit_price < 0:
            raise HTTPException(
                status_code=400,
                detail="Đơn giá không được âm"
            )

        line_subtotal = item.quantity * item.unit_price
        line_tax = line_subtotal * item.tax_rate / Decimal("100")
        line_total = line_subtotal + line_tax

        subtotal += line_subtotal
        tax_amount += line_tax

        return_items.append(
            SalesReturnItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                tax_rate=item.tax_rate,
                line_subtotal=line_subtotal,
                line_tax=line_tax,
                line_total=line_total
            )
        )

    total_amount = subtotal + tax_amount

    if tax_amount > 0 and data.tax_account_id is None:
        raise HTTPException(
            status_code=400,
            detail="Phiếu trả hàng có thuế nhưng chưa chọn tài khoản thuế"
        )

    journal = JournalEntry(
        entry_date=data.return_date,
        description=data.description or f"Trả hàng bán {data.return_no}",
        status="posted"
    )

    # Nợ 5212 - Hàng bán bị trả lại
    journal.lines.append(
        JournalEntryLine(
            account_id=data.sales_return_account_id,
            debit=subtotal,
            credit=Decimal("0")
        )
    )

    # Nợ 3331 - Giảm thuế GTGT phải nộp
    if tax_amount > 0:
        journal.lines.append(
            JournalEntryLine(
                account_id=data.tax_account_id,
                debit=tax_amount,
                credit=Decimal("0")
            )
        )

    # Có 131 - Giảm phải thu khách hàng
    journal.lines.append(
        JournalEntryLine(
            account_id=data.receivable_account_id,
            debit=Decimal("0"),
            credit=total_amount
        )
    )

    db.add(journal)
    db.flush()

    sales_return = SalesReturn(
        return_no=data.return_no,
        return_date=data.return_date,
        sales_invoice_id=data.sales_invoice_id,
        customer_id=data.customer_id,
        description=data.description,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,
        receivable_account_id=data.receivable_account_id,
        sales_return_account_id=data.sales_return_account_id,
        tax_account_id=data.tax_account_id,
        journal_entry_id=journal.id
    )

    for return_item in return_items:
        sales_return.items.append(return_item)

    db.add(sales_return)
    db.commit()
    db.refresh(sales_return)

    return sales_return


@router.get("/", response_model=list[SalesReturnResponse])
def get_sales_returns(
    db: Session = Depends(get_db)
):
    return (
        db.query(SalesReturn)
        .order_by(SalesReturn.id.desc())
        .all()
    )


@router.get("/{sales_return_id}", response_model=SalesReturnResponse)
def get_sales_return(
    sales_return_id: int,
    db: Session = Depends(get_db)
):
    sales_return = db.query(SalesReturn).filter(
        SalesReturn.id == sales_return_id
    ).first()

    if not sales_return:
        raise HTTPException(
            status_code=404,
            detail="Phiếu trả hàng bán không tồn tại"
        )

    return sales_return