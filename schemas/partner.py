from pydantic import BaseModel, EmailStr


class CustomerCreate(BaseModel):
    code: str
    name: str
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    tax_code: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    tax_code: str | None = None
    is_active: bool | None = None


class CustomerResponse(BaseModel):
    id: int
    code: str
    name: str
    phone: str | None
    email: str | None
    address: str | None
    tax_code: str | None
    is_active: bool

    model_config = {
        "from_attributes": True
    }


class SupplierCreate(BaseModel):
    code: str
    name: str
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    tax_code: str | None = None


class SupplierUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    tax_code: str | None = None
    is_active: bool | None = None


class SupplierResponse(BaseModel):
    id: int
    code: str
    name: str
    phone: str | None
    email: str | None
    address: str | None
    tax_code: str | None
    is_active: bool

    model_config = {
        "from_attributes": True
    }