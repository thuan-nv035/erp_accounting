from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.account import Account
from models.partner import Customer, Supplier
from models.journal import JournalEntry, JournalEntryLine
from models.payment import Payment, SupplierPayment
from models.purchase_invoice import PurchaseInvoice
from schemas.payment import ReceivePaymentCreate, PaySupplierCreate


def receive_payment(db: Session, data: ReceivePaymentCreate):
    if data.amount <= Decimal("0"):
        raise HTTPException(
            status_code=400,
            detail="Số tiền thanh toán phải lớn hơn 0"
        )

    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Khách hàng không tồn tại"
        )

    cash_account = db.query(Account).filter(
        Account.id == data.cash_account_id
    ).first()

    if not cash_account:
        raise HTTPException(
            status_code=404,
            detail="Tài khoản tiền mặt/ngân hàng không tồn tại"
        )

    receivable_account = db.query(Account).filter(
        Account.id == data.receivable_account_id
    ).first()

    if not receivable_account:
        raise HTTPException(
            status_code=404,
            detail="Tài khoản phải thu không tồn tại"
        )

    existed_payment = db.query(Payment).filter(
        Payment.payment_no == data.payment_no
    ).first()

    if existed_payment:
        raise HTTPException(
            status_code=400,
            detail="Số phiếu thu đã tồn tại"
        )

    journal = JournalEntry(
        entry_date=data.payment_date,
        description=data.description or f"Thu tiền khách hàng {customer.name}",
        status="posted"
    )

    journal.lines.append(
        JournalEntryLine(
            account_id=data.cash_account_id,
            debit=data.amount,
            credit=Decimal("0")
        )
    )

    journal.lines.append(
        JournalEntryLine(
            account_id=data.receivable_account_id,
            debit=Decimal("0"),
            credit=data.amount
        )
    )

    db.add(journal)
    db.flush()

    payment = Payment(
        payment_no=data.payment_no,
        payment_date=data.payment_date,
        invoice_id=data.invoice_id,
        customer_id=data.customer_id,
        cash_account_id=data.cash_account_id,
        receivable_account_id=data.receivable_account_id,
        amount=data.amount,
        payment_method=data.payment_method,
        description=data.description,
        journal_entry_id=journal.id
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment

def pay_supplier(db: Session, data: PaySupplierCreate):
    if data.amount <= Decimal("0"):
        raise HTTPException(
            status_code=400,
            detail="Số tiền chi phải lớn hơn 0"
        )

    existed_payment = db.query(SupplierPayment).filter(
        SupplierPayment.payment_no == data.payment_no
    ).first()

    if existed_payment:
        raise HTTPException(
            status_code=400,
            detail="Số phiếu chi đã tồn tại"
        )

    supplier = db.query(Supplier).filter(
        Supplier.id == data.supplier_id
    ).first()

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Nhà cung cấp/đối tác không tồn tại"
        )

    cash_account = db.query(Account).filter(
        Account.id == data.cash_account_id
    ).first()

    if not cash_account:
        raise HTTPException(
            status_code=404,
            detail="Tài khoản tiền mặt/ngân hàng không tồn tại"
        )

    payable_account = db.query(Account).filter(
        Account.id == data.payable_account_id
    ).first()

    if not payable_account:
        raise HTTPException(
            status_code=404,
            detail="Tài khoản phải trả nhà cung cấp không tồn tại"
        )

    purchase_invoice = None

    if data.purchase_invoice_id is not None:
        purchase_invoice = db.query(PurchaseInvoice).filter(
            PurchaseInvoice.id == data.purchase_invoice_id
        ).first()

        if not purchase_invoice:
            raise HTTPException(
                status_code=404,
                detail="Hóa đơn mua hàng không tồn tại"
            )

    journal = JournalEntry(
        entry_date=data.payment_date,
        description=data.description or f"Chi tiền cho nhà cung cấp {supplier.name}",
        status="posted"
    )

    journal.lines.append(
        JournalEntryLine(
            account_id=data.payable_account_id,
            debit=data.amount,
            credit=Decimal("0")
        )
    )

    journal.lines.append(
        JournalEntryLine(
            account_id=data.cash_account_id,
            debit=Decimal("0"),
            credit=data.amount
        )
    )

    db.add(journal)
    db.flush()

    supplier_payment = SupplierPayment(
        payment_no=data.payment_no,
        payment_date=data.payment_date,
        purchase_invoice_id=data.purchase_invoice_id,
        supplier_id=data.supplier_id,
        cash_account_id=data.cash_account_id,
        payable_account_id=data.payable_account_id,
        amount=data.amount,
        payment_method=data.payment_method,
        description=data.description,
        journal_entry_id=journal.id
    )

    db.add(supplier_payment)
    db.commit()
    db.refresh(supplier_payment)

    return supplier_payment