import sqlite3
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status

from app.models import Product, SalesReport
from app.repository import list_sales_products

router = APIRouter(prefix="/reports", tags=["reports"])


def calculate_total(formula: Literal["total"], items: list[Product]) -> float:
    if formula == "total":
        return sum((item.price for item in items), start=0.0)

    raise AssertionError("Unsupported formula")


@router.get("/sales", response_model=SalesReport)
def sales_report(
    category: str = Query(min_length=1, max_length=100),
    formula: Literal["total"] = Query(default="total"),
) -> SalesReport:
    try:
        items = list_sales_products(category)
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate sales report",
        ) from exc

    return SalesReport(
        category=category,
        items=items,
        total=calculate_total(formula, items),
    )
