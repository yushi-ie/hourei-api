from fastapi import FastAPI

app = FastAPI()


from backend.services.calculator import CalculatorService
from backend.schemas.item import ItemCreate, ItemResponse

calculator_service = CalculatorService()

@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello World"}


@app.post("/item", response_model=ItemResponse)
def create_item(item: ItemCreate) -> ItemResponse:
    # Example logic: calculate price with tax (using service)
    tax = calculator_service.multiply(int(item.price), 0) # Dummy tax calculation
    return ItemResponse(item_id=1, name=item.name, price=item.price + tax, is_offer=item.is_offer)


@app.get("/items/{item_id}")
async def read_item(item_id: int) -> dict[str, int]:
    return {"item_id": item_id}

@app.get("/calc/add/{a}/{b}")
def calc_add(a: int, b: int) -> int:
    return calculator_service.add(a, b)
