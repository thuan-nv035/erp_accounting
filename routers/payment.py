from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.payment import Payment
from schemas.payment import ReceivePaymentCreate, PaymentResponse, SupplierPaymentResponse, PaySupplierCreate
from services.payment_service import receive_payment, pay_supplier

router = APIRouter(
    prefix="/api/v1/payments",
    tags=["Payments"]
)


@router.post("/receive", response_model=PaymentResponse)
def create_receive_payment(
    data: ReceivePaymentCreate,
    db: Session = Depends(get_db)
):
    return receive_payment(db, data)


@router.get("/", response_model=list[PaymentResponse])
def get_payments(db: Session = Depends(get_db)):
    return db.query(Payment).order_by(Payment.id.desc()).all()

@router.post("/pay", response_model=SupplierPaymentResponse)
def create_supplier_payment(
    data: PaySupplierCreate,
    db: Session = Depends(get_db)
):
    return pay_supplier(db, data)