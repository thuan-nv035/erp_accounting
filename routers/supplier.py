from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.partner import Supplier
from schemas.partner import SupplierCreate, SupplierUpdate, SupplierResponse

router = APIRouter(
    prefix="/api/v1/suppliers",
    tags=["Suppliers"]
)


@router.post("/", response_model=SupplierResponse)
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db)):
    exists = db.query(Supplier).filter(Supplier.code == data.code).first()

    if exists:
        raise HTTPException(
            status_code=400,
            detail="Mã nhà cung cấp đã tồn tại"
        )

    supplier = Supplier(**data.model_dump())

    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    return supplier


@router.get("/", response_model=list[SupplierResponse])
def get_suppliers(db: Session = Depends(get_db)):
    return db.query(Supplier).order_by(Supplier.id.desc()).all()


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy nhà cung cấp"
        )

    return supplier


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    db: Session = Depends(get_db)
):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy nhà cung cấp"
        )

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(supplier, key, value)

    db.commit()
    db.refresh(supplier)

    return supplier


@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy nhà cung cấp"
        )

    db.delete(supplier)
    db.commit()

    return {
        "message": "Đã xóa nhà cung cấp"
    }