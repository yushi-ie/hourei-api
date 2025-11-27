from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_read_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_create_item() -> None:
    response = client.post("/item", json={"name": "test", "price": 100.0})
    assert response.status_code == 200
    assert response.json()["name"] == "test"
    assert response.json()["price"] == 100.0


def test_read_item() -> None:
    response = client.get("/items/42")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42}

def test_calc_add() -> None:
    response = client.get("/calc/add/2/3")
    assert response.status_code == 200
    assert response.json() == 5
