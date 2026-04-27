from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.account import Account
from models.partner import Customer
from models.product import Product
from models.journal import JournalEntry, JournalEntryLine
from models.sales_invoice import SalesInvoice, SalesInvoiceItem
from schemas.sales_invoice import SalesInvoiceCreate, SalesInvoiceResponse

router = APIRouter(
    prefix="/api/v1/sales-invoices",
    tags=["Sales Invoices"]
)


@router.post("/", response_model=SalesInvoiceResponse)
def create_sales_invoice(data: SalesInvoiceCreate, db: Session = Depends(get_db)):
    exists = db.query(SalesInvoice).filter(
        SalesInvoice.invoice_no == data.invoice_no
    ).first()

    if exists:
        raise HTTPException(
            status_code=400,
            detail="Số hóa đơn đã tồn tại"
        )

    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Khách hàng không tồn tại"
        )

    if len(data.items) == 0:
        raise HTTPException(
            status_code=400,
            detail="Hóa đơn phải có ít nhất 1 sản phẩm"
        )

    receivable_account = db.query(Account).filter(
        Account.id == data.receivable_account_id
    ).first()

    revenue_account = db.query(Account).filter(
        Account.id == data.revenue_account_id
    ).first()

    if not receivable_account:
        raise HTTPException(
            status_code=400,
            detail="Tài khoản phải thu không tồn tại"
        )

    if not revenue_account:
        raise HTTPException(
            status_code=400,
            detail="Tài khoản doanh thu không tồn tại"
        )

    tax_account = None

    if data.tax_account_id:
        tax_account = db.query(Account).filter(
            Account.id == data.tax_account_id
        ).first()

        if not tax_account:
            raise HTTPException(
                status_code=400,
                detail="Tài khoản thuế không tồn tại"
            )

    subtotal = Decimal("0.00")
    vat_amount = Decimal("0.00")
    total_amount = Decimal("0.00")

    invoice_items = []

    for item in data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Sản phẩm id={item.product_id} không tồn tại"
            )

        if item.quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail="Số lượng phải lớn hơn 0"
            )

        if item.unit_price < 0:
            raise HTTPException(
                status_code=400,
                detail="Đơn giá không được âm"
            )

        line_subtotal = item.quantity * item.unit_price
        line_vat = line_subtotal * item.vat_rate / Decimal("100")
        line_total = line_subtotal + line_vat

        subtotal += line_subtotal
        vat_amount += line_vat
        total_amount += line_total

        invoice_items.append(
            SalesInvoiceItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                vat_rate=item.vat_rate,
                line_subtotal=line_subtotal,
                line_vat=line_vat,
                line_total=line_total
            )
        )

    if vat_amount > 0 and not tax_account:
        raise HTTPException(
            status_code=400,
            detail="Hóa đơn có VAT thì phải truyền tax_account_id"
        )

    journal = JournalEntry(
        entry_date=data.invoice_date,
        description=f"Hóa đơn bán hàng {data.invoice_no}",
        status="posted"
    )

    journal.lines.append(
        JournalEntryLine(
            account_id=data.receivable_account_id,
            debit=total_amount,
            credit=Decimal("0.00")
        )
    )

    journal.lines.append(
        JournalEntryLine(
            account_id=data.revenue_account_id,
            debit=Decimal("0.00"),
            credit=subtotal
        )
    )

    if vat_amount > 0:
        journal.lines.append(
            JournalEntryLine(
                account_id=data.tax_account_id,
                debit=Decimal("0.00"),
                credit=vat_amount
            )
        )

    invoice = SalesInvoice(
        invoice_no=data.invoice_no,
        customer_id=data.customer_id,
        invoice_date=data.invoice_date,
        due_date=data.due_date,
        description=data.description,
        status="posted",
        subtotal=subtotal,
        vat_amount=vat_amount,
        total_amount=total_amount
    )

    invoice.items = invoice_items

    db.add(journal)
    db.flush()

    invoice.journal_entry_id = journal.id

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return invoice


@router.get("/", response_model=list[SalesInvoiceResponse])
def get_sales_invoices(db: Session = Depends(get_db)):
    return db.query(SalesInvoice).order_by(SalesInvoice.id.desc()).all()


@router.get("/{invoice_id}", response_model=SalesInvoiceResponse)
def get_sales_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(SalesInvoice).filter(
        SalesInvoice.id == invoice_id
    ).first()

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy hóa đơn bán hàng"
        )

    return invoice