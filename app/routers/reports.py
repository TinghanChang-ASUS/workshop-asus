import sqlite3
from enum import Enum
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.models import SalesReport
from app.repository import get_sales_report

router = APIRouter(prefix="/reports", tags=["reports"])


class SalesFormula(str, Enum):
    total = "total"


@router.get("/sales", response_model=SalesReport)
def read_sales_report(
    category: Annotated[str, Query(min_length=1, max_length=100)],
    formula: SalesFormula = Query(default=SalesFormula.total),
) -> SalesReport:
    try:
        items, total = get_sales_report(category)
    except sqlite3.Error as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate sales report",
        ) from error

    return SalesReport(
        category=category,
        items=items,
        total=total if formula is SalesFormula.total else total,
    )
