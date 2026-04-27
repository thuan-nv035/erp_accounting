from pydantic import BaseModel


class AccountCreate(BaseModel):
    code: str
    name: str
    type: str


class AccountResponse(BaseModel):
    id: int
    code: str
    name: str
    type: str
    is_active: bool

    model_config = {
        "from_attributes": True
    }