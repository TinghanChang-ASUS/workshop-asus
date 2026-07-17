import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.routers import reports


def test_sales_report_returns_matching_items_and_total(client: TestClient) -> None:
    response = client.get("/reports/sales", params={"category": "Laptop"})

    assert response.status_code == 200
    assert response.json() == {
        "category": "Laptop",
        "items": [
            {
                "id": 1,
                "name": "Zenbook 14 OLED",
                "category": "Laptop",
                "price": 42900.0,
            }
        ],
        "total": 42900.0,
    }


def test_sales_report_blocks_sql_injection(client: TestClient) -> None:
    response = client.get(
        "/reports/sales",
        params={"category": "Laptop' OR '1'='1"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "category": "Laptop' OR '1'='1",
        "items": [],
        "total": 0.0,
    }


def test_sales_report_blocks_formula_code_injection(client: TestClient) -> None:
    response = client.get(
        "/reports/sales",
        params={"category": "Laptop", "formula": "__import__('os').system('id')"},
    )

    assert response.status_code == 422
    assert "total" in response.text


def test_sales_report_hides_internal_errors(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_database_error(category: str) -> list[object]:
        raise sqlite3.OperationalError("Traceback: /tmp/private.db")

    monkeypatch.setattr(reports, "list_sales_products", raise_database_error)

    response = client.get("/reports/sales", params={"category": "Laptop"})

    assert response.status_code == 500
    assert response.json() == {"detail": "Could not generate sales report"}
    assert "Traceback" not in response.text
    assert "/tmp/private.db" not in response.text
