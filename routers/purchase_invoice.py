from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db

from models.account import Account
from models.partner import Supplier
from models.product import Product
from models.journal import JournalEntry, JournalEntryLine
from models.purchase_invoice import PurchaseInvoice, PurchaseInvoiceItem

from schemas.purchase_invoice import (
    PurchaseInvoiceCreate,
    PurchaseInvoiceResponse
)


router = APIRouter(
    prefix="/api/v1/purchase-invoices",
    tags=["Purchase Invoices"]
)


@router.post("/", response_model=PurchaseInvoiceResponse)
def create_purchase_invoice(
    data: PurchaseInvoiceCreate,
    db: Session = Depends(get_db)
):
    existed_invoice = db.query(PurchaseInvoice).filter(
        PurchaseInvoice.invoice_no == data.invoice_no
    ).first()

    if existed_invoice:
        raise HTTPException(
            status_code=400,
            detail="Số hóa đơn mua hàng đã tồn tại"
        )

    supplier = db.query(Supplier).filter(
        Supplier.id == data.supplier_id
    ).first()

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Nhà cung cấp/đối tác không tồn tại"
        )

    purchase_account = db.query(Account).filter(
        Account.id == data.purchase_account_id
    ).first()

    if not purchase_account:
        raise HTTPException(
            status_code=404,
            detail="Tài khoản mua hàng/hàng hóa không tồn tại"
        )

    payable_account = db.query(Account).filter(
        Account.id == data.payable_account_id
    ).first()

    if not payable_account:
        raise HTTPException(
            status_code=404,
            detail="Tài khoản phải trả không tồn tại"
        )

    tax_account = None

    if data.tax_account_id is not None:
        tax_account = db.query(Account).filter(
            Account.id == data.tax_account_id
        ).first()

        if not tax_account:
            raise HTTPException(
                status_code=404,
                detail="Tài khoản thuế GTGT đầu vào không tồn tại"
            )

    if not data.items:
        raise HTTPException(
            status_code=400,
            detail="Hóa đơn phải có ít nhất 1 sản phẩm"
        )

    subtotal = Decimal("0")
    tax_amount = Decimal("0")

    invoice_items = []

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
                detail="Số lượng sản phẩm phải lớn hơn 0"
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

        invoice_items.append(
            PurchaseInvoiceItem(
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

    journal = JournalEntry(
        entry_date=data.invoice_date,
        description=data.description or f"Hóa đơn mua hàng {data.invoice_no}",
        status="posted"
    )

    journal.lines.append(
        JournalEntryLine(
            account_id=data.purchase_account_id,
            debit=subtotal,
            credit=Decimal("0")
        )
    )

    if tax_amount > 0:
        if data.tax_account_id is None:
            raise HTTPException(
                status_code=400,
                detail="Hóa đơn có thuế nhưng chưa chọn tài khoản thuế GTGT đầu vào"
            )

        journal.lines.append(
            JournalEntryLine(
                account_id=data.tax_account_id,
                debit=tax_amount,
                credit=Decimal("0")
            )
        )

    journal.lines.append(
        JournalEntryLine(
            account_id=data.payable_account_id,
            debit=Decimal("0"),
            credit=total_amount
        )
    )

    db.add(journal)
    db.flush()

    invoice = PurchaseInvoice(
        invoice_no=data.invoice_no,
        supplier_id=data.supplier_id,
        invoice_date=data.invoice_date,
        due_date=data.due_date,
        description=data.description,

        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,

        purchase_account_id=data.purchase_account_id,
        tax_account_id=data.tax_account_id,
        payable_account_id=data.payable_account_id,

        journal_entry_id=journal.id
    )

    for invoice_item in invoice_items:
        invoice.items.append(invoice_item)

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return invoice


@router.get("/", response_model=list[PurchaseInvoiceResponse])
def get_purchase_invoices(
    db: Session = Depends(get_db)
):
    return (
        db.query(PurchaseInvoice)
        .order_by(PurchaseInvoice.id.desc())
        .all()
    )


@router.get("/{invoice_id}", response_model=PurchaseInvoiceResponse)
def get_purchase_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    invoice = db.query(PurchaseInvoice).filter(
        PurchaseInvoice.id == invoice_id
    ).first()

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Hóa đơn mua hàng không tồn tại"
        )

    return invoice