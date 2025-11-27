from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None

class ItemResponse(BaseModel):
    item_id: int
    name: str
    price: float
    is_offer: bool | None = None
