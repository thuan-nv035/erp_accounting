from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from models.sales_return import SalesReturnItem, SalesReturn
from database import get_db
from models.account import Account
from models.journal import JournalEntryLine, JournalEntry
from models.payment import Payment, SupplierPayment
from models.product import Product
from models.purchase_invoice import PurchaseInvoice, PurchaseInvoiceItem
from models.sales_invoice import SalesInvoice, SalesInvoiceItem
from models.stock_adjustment import StockAdjustmentItem, StockAdjustment
from schemas.report import TrialBalanceResponse, TrialBalanceItem, ProfitLossResponse, BalanceSheetResponse, \
    ReceivablesResponse, PayablesResponse, InventoryReportResponse

router = APIRouter(
    prefix="/api/v1/reports",
    tags=["Reports"]
)


@router.get("/trial-balance", response_model=TrialBalanceResponse)
def get_trial_balance(db: Session = Depends(get_db)):
    accounts = db.query(Account).order_by(Account.code.asc()).all()

    items = []

    total_debit_all = Decimal("0.00")
    total_credit_all = Decimal("0.00")
    total_debit_balance = Decimal("0.00")
    total_credit_balance = Decimal("0.00")

    for account in accounts:
        lines = db.query(JournalEntryLine).filter(
            JournalEntryLine.account_id == account.id
        ).all()

        total_debit = sum(
            (line.debit or Decimal("0.00")) for line in lines
        )

        total_credit = sum(
            (line.credit or Decimal("0.00")) for line in lines
        )

        balance = total_debit - total_credit

        if balance >= 0:
            debit_balance = balance
            credit_balance = Decimal("0.00")
        else:
            debit_balance = Decimal("0.00")
            credit_balance = abs(balance)

        total_debit_all += total_debit
        total_credit_all += total_credit
        total_debit_balance += debit_balance
        total_credit_balance += credit_balance

        items.append(
            TrialBalanceItem(
                account_id=account.id,
                account_code=account.code,
                account_name=account.name,
                account_type=account.type,
                total_debit=total_debit,
                total_credit=total_credit,
                debit_balance=debit_balance,
                credit_balance=credit_balance
            )
        )

    return TrialBalanceResponse(
        total_debit=total_debit_all,
        total_credit=total_credit_all,
        total_debit_balance=total_debit_balance,
        total_credit_balance=total_credit_balance,
        is_balanced=total_debit_all == total_credit_all,
        items=items
    )

@router.get("/profit-loss", response_model=ProfitLossResponse)
def get_profit_loss(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db)
):
    accounts = (
        db.query(Account)
        .filter(Account.type.in_(["revenue", "expense"]))
        .order_by(Account.code.asc())
        .all()
    )

    result_lines = []

    total_revenue = Decimal("0")
    total_expense = Decimal("0")

    for account in accounts:
        query = (
            db.query(JournalEntryLine, JournalEntry)
            .join(
                JournalEntry,
                JournalEntry.id == JournalEntryLine.journal_entry_id
            )
            .filter(JournalEntryLine.account_id == account.id)
        )

        if date_from:
            query = query.filter(JournalEntry.entry_date >= date_from)

        if date_to:
            query = query.filter(JournalEntry.entry_date <= date_to)

        rows = query.all()

        total_debit = Decimal("0")
        total_credit = Decimal("0")

        for line, journal in rows:
            total_debit += line.debit or Decimal("0")
            total_credit += line.credit or Decimal("0")

        if account.type == "revenue":
            amount = total_credit - total_debit
            total_revenue += amount

        elif account.type == "expense":
            amount = total_debit - total_credit
            total_expense += amount

        else:
            amount = Decimal("0")

        if amount == 0:
            continue

        result_lines.append({
            "account_id": account.id,
            "account_code": account.code,
            "account_name": account.name,
            "account_type": account.type,
            "amount": amount
        })

    net_profit = total_revenue - total_expense

    return {
        "date_from": date_from,
        "date_to": date_to,
        "total_revenue": total_revenue,
        "total_expense": total_expense,
        "net_profit": net_profit,
        "lines": result_lines
    }

@router.get("/balance-sheet", response_model=BalanceSheetResponse)
def get_balance_sheet(
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db)
):
    accounts = (
        db.query(Account)
        .filter(Account.type.in_(["asset", "liability", "equity"]))
        .order_by(Account.code.asc())
        .all()
    )

    asset_lines = []
    liability_lines = []
    equity_lines = []

    total_assets = Decimal("0")
    total_liabilities = Decimal("0")
    total_equity = Decimal("0")

    for account in accounts:
        query = (
            db.query(JournalEntryLine, JournalEntry)
            .join(
                JournalEntry,
                JournalEntry.id == JournalEntryLine.journal_entry_id
            )
            .filter(JournalEntryLine.account_id == account.id)
        )

        if date_to:
            query = query.filter(JournalEntry.entry_date <= date_to)

        rows = query.all()

        total_debit = Decimal("0")
        total_credit = Decimal("0")

        for line, journal in rows:
            total_debit += line.debit or Decimal("0")
            total_credit += line.credit or Decimal("0")

        if account.type == "asset":
            balance = total_debit - total_credit
        elif account.type in ["liability", "equity"]:
            balance = total_credit - total_debit
        else:
            balance = Decimal("0")

        if balance == 0:
            continue

        line_data = {
            "account_id": account.id,
            "account_code": account.code,
            "account_name": account.name,
            "account_type": account.type,
            "balance": balance
        }

        if account.type == "asset":
            asset_lines.append(line_data)
            total_assets += balance

        elif account.type == "liability":
            liability_lines.append(line_data)
            total_liabilities += balance

        elif account.type == "equity":
            equity_lines.append(line_data)
            total_equity += balance

    total_liabilities_and_equity = total_liabilities + total_equity

    return {
        "date_to": date_to,

        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "total_equity": total_equity,
        "total_liabilities_and_equity": total_liabilities_and_equity,

        "is_balanced": total_assets == total_liabilities_and_equity,

        "assets": {
            "total": total_assets,
            "lines": asset_lines
        },
        "liabilities": {
            "total": total_liabilities,
            "lines": liability_lines
        },
        "equity": {
            "total": total_equity,
            "lines": equity_lines
        }
    }

@router.get("/receivables", response_model=ReceivablesResponse)
def get_receivables(
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db)
):
    query = db.query(SalesInvoice)

    if date_to:
        query = query.filter(SalesInvoice.invoice_date <= date_to)

    invoices = query.order_by(SalesInvoice.invoice_date.asc()).all()

    lines = []

    total_invoiced = Decimal("0")
    total_paid = Decimal("0")
    total_balance = Decimal("0")

    for invoice in invoices:
        payments = db.query(Payment).filter(
            Payment.invoice_id == invoice.id
        ).all()

        paid_amount = Decimal("0")

        for payment in payments:
            paid_amount += payment.amount or Decimal("0")

        returns = db.query(SalesReturn).filter(
            SalesReturn.sales_invoice_id == invoice.id
        ).all()

        returned_amount = Decimal("0")

        for sales_return in returns:
            returned_amount += sales_return.total_amount or Decimal("0")

        total_amount = invoice.total_amount or Decimal("0")
        balance = total_amount - returned_amount - paid_amount

        if balance <= 0:
            status = "paid"
        elif paid_amount > 0:
            status = "partial"
        else:
            status = "unpaid"

        total_invoiced += total_amount
        total_paid += paid_amount
        total_balance += balance

        lines.append({
            "invoice_id": invoice.id,
            "invoice_no": invoice.invoice_no,
            "customer_id": invoice.customer_id,
            "invoice_date": invoice.invoice_date,
            "due_date": invoice.due_date,
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "balance": balance,
            "status": status
        })

    return {
        "date_to": date_to,
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "total_balance": total_balance,
        "lines": lines
    }

@router.get("/payables", response_model=PayablesResponse)
def get_payables(
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db)
):
    query = db.query(PurchaseInvoice)

    if date_to:
        query = query.filter(PurchaseInvoice.invoice_date <= date_to)

    invoices = query.order_by(PurchaseInvoice.invoice_date.asc()).all()

    lines = []

    total_invoiced = Decimal("0")
    total_paid = Decimal("0")
    total_balance = Decimal("0")

    for invoice in invoices:
        payments = db.query(SupplierPayment).filter(
            SupplierPayment.purchase_invoice_id == invoice.id
        ).all()

        paid_amount = Decimal("0")

        for payment in payments:
            paid_amount += payment.amount or Decimal("0")

        total_amount = invoice.total_amount or Decimal("0")
        balance = total_amount - paid_amount

        if balance <= 0:
            status = "paid"
        elif paid_amount > 0:
            status = "partial"
        else:
            status = "unpaid"

        total_invoiced += total_amount
        total_paid += paid_amount
        total_balance += balance

        lines.append({
            "invoice_id": invoice.id,
            "invoice_no": invoice.invoice_no,
            "supplier_id": invoice.supplier_id,
            "invoice_date": invoice.invoice_date,
            "due_date": invoice.due_date,
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "balance": balance,
            "status": status
        })

    return {
        "date_to": date_to,
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "total_balance": total_balance,
        "lines": lines
    }

@router.get("/inventory", response_model=InventoryReportResponse)
def get_inventory_report(
    db: Session = Depends(get_db)
):
    products = db.query(Product).order_by(Product.id.asc()).all()

    lines = []
    total_inventory_value = Decimal("0")

    for product in products:
        purchase_items = db.query(PurchaseInvoiceItem).filter(
            PurchaseInvoiceItem.product_id == product.id
        ).all()

        sales_items = db.query(SalesInvoiceItem).filter(
            SalesInvoiceItem.product_id == product.id
        ).all()

        purchased_qty = Decimal("0")
        purchased_value = Decimal("0")

        for item in purchase_items:
            qty = item.quantity or Decimal("0")
            line_subtotal = item.line_subtotal or Decimal("0")

            purchased_qty += qty
            purchased_value += line_subtotal

        sold_qty = Decimal("0")

        for item in sales_items:
            qty = item.quantity or Decimal("0")
            sold_qty += qty

        sales_return_items = db.query(SalesReturnItem).filter(
            SalesReturnItem.product_id == product.id
        ).all()

        sales_return_qty = Decimal("0")

        for item in sales_return_items:
            sales_return_qty += item.quantity or Decimal("0")

        adjustment_items = (
            db.query(StockAdjustmentItem, StockAdjustment)
            .join(
                StockAdjustment,
                StockAdjustment.id == StockAdjustmentItem.adjustment_id
            )
            .filter(StockAdjustmentItem.product_id == product.id)
            .all()
        )

        adjustment_in_qty = Decimal("0")
        adjustment_out_qty = Decimal("0")
        adjustment_in_value = Decimal("0")
        adjustment_out_value = Decimal("0")

        for adj_item, adj in adjustment_items:
            qty = adj_item.quantity or Decimal("0")
            value = adj_item.line_value or Decimal("0")

            if adj.adjustment_type == "increase":
                adjustment_in_qty += qty
                adjustment_in_value += value
            elif adj.adjustment_type == "decrease":
                adjustment_out_qty += qty
                adjustment_out_value += value

        ending_qty = purchased_qty + adjustment_in_qty + sales_return_qty - sold_qty - adjustment_out_qty

        if purchased_qty > 0:
            avg_purchase_price = purchased_value / purchased_qty
        else:
            avg_purchase_price = Decimal("0")

        inventory_value = ending_qty * avg_purchase_price

        if purchased_qty == 0 and sold_qty == 0:
            continue

        total_inventory_value += inventory_value

        # purchased_qty = Tổng số lượng mua vào
        # sold_qty = Tổng số lượng bán ra
        # ending_qty = Số lượng tồn kho
        # avg_purchase_price = Giá mua trung bình
        # inventory_value = Giá trị tồn kho

        lines.append({
            "product_id": product.id,
            "product_name": product.name,
            "purchased_qty": purchased_qty,
            "sold_qty": sold_qty,
            "ending_qty": ending_qty,
            "avg_purchase_price": avg_purchase_price,
            "inventory_value": inventory_value
        })

    return {
        "total_inventory_value": total_inventory_value,
        "lines": lines
    }