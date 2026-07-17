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


def test_sales_report_treats_sql_injection_as_plain_text(client: TestClient) -> None:
    response = client.get(
        "/reports/sales",
        params={"category": "Laptop' OR 1=1 --"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "category": "Laptop' OR 1=1 --",
        "items": [],
        "total": 0.0,
    }


def test_sales_report_rejects_formula_code_injection(client: TestClient) -> None:
    response = client.get(
        "/reports/sales",
        params={"category": "Laptop", "formula": "__import__('os').system('id')"},
    )

    assert response.status_code == 422


def test_sales_report_hides_internal_errors(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_database_error(category: str) -> tuple[list[object], float]:
        raise sqlite3.OperationalError("stack trace details should stay private")

    monkeypatch.setattr(reports, "get_sales_report", raise_database_error)

    response = client.get("/reports/sales", params={"category": "Laptop"})

    assert response.status_code == 500
    assert response.json() == {"detail": "Unable to generate sales report"}
