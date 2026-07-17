import pytest
from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_products(client: TestClient) -> None:
    response = client.get("/products")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 6
    assert body["page"] == 1
    assert body["page_size"] == 20
    assert body["items"][0]["name"] == "Zenbook 14 OLED"


def test_list_products_can_search_by_name_or_category(client: TestClient) -> None:
    response = client.get("/products", params={"q": "gaming"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert [item["name"] for item in body["items"]] == [
        "ROG Zephyrus G14",
        "TUF Gaming A15",
    ]


def test_list_products_can_sort_by_price_descending(client: TestClient) -> None:
    response = client.get("/products", params={"sort": "price", "order": "desc"})

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["items"][:3]] == [3, 2, 1]


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0},
        {"page_size": 0},
        {"page_size": 21},
        {"q": ""},
        {"q": "x" * 101},
    ],
)
def test_list_products_rejects_invalid_query_parameter_values(
    client: TestClient,
    params: dict[str, object],
) -> None:
    response = client.get("/products", params=params)

    assert response.status_code == 422


def test_get_product(client: TestClient) -> None:
    response = client.get("/products/2")

    assert response.status_code == 200
    assert response.json()["name"] == "ROG Zephyrus G14"


def test_get_missing_product(client: TestClient) -> None:
    response = client.get("/products/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}
