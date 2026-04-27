from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from database import get_db
from models.account import Account
from schemas.account import AccountResponse, AccountCreate

router = APIRouter(
    prefix="/api/v1/accounts",
    tags=["Accounts"]
)

@router.post("/", response_model=AccountResponse)
def create_account(data: AccountCreate, db: Session = Depends(get_db)):
    account = Account(
        code=data.code,
        name=data.name,
        type=data.type
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account


@router.get("/", response_model=list[AccountResponse])
def get_accounts(db: Session = Depends(get_db)):
    return db.query(Account).order_by(Account.code).all()