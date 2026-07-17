import sqlite3
from typing import Literal

from app.models import Product

PRODUCTS = [
    Product(id=1, name="Zenbook 14 OLED", category="Laptop", price=42900),
    Product(id=2, name="ROG Zephyrus G14", category="Gaming Laptop", price=62900),
    Product(id=3, name="ProArt P16", category="Creator Laptop", price=79900),
    Product(id=4, name="TUF Gaming A15", category="Gaming Laptop", price=38900),
    Product(id=5, name="ROG Ally X", category="Handheld", price=26900),
    Product(id=6, name="ProArt Display PA279CRV", category="Monitor", price=15900),
]


SortField = Literal["id", "name", "category", "price"]
SortOrder = Literal["asc", "desc"]


def list_products(
    *,
    q: str | None = None,
    sort: SortField = "id",
    order: SortOrder = "asc",
    page: int = 1,
    page_size: int = 20,
) -> list[Product]:
    products = sorted(
        _filter_products(q=q),
        key=lambda product: getattr(product, sort),
        reverse=order == "desc",
    )

    start = (page - 1) * page_size
    end = start + page_size
    return products[start:end]


def count_products(*, q: str | None = None) -> int:
    return len(_filter_products(q=q))


def get_product(product_id: int) -> Product | None:
    return next((product for product in PRODUCTS if product.id == product_id), None)


def create_sales_report_database() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute("CREATE TABLE products (id INTEGER, name TEXT, category TEXT, price REAL)")
    connection.executemany(
        "INSERT INTO products VALUES (?, ?, ?, ?)",
        [(product.id, product.name, product.category, product.price) for product in PRODUCTS],
    )
    return connection


def get_sales_report(category: str) -> tuple[list[Product], float]:
    connection = create_sales_report_database()
    try:
        rows = connection.execute(
            "SELECT id, name, category, price FROM products WHERE category = ?",
            (category,),
        ).fetchall()
    finally:
        connection.close()

    items = [Product.model_validate(dict(row)) for row in rows]
    total = sum(item.price for item in items)
    return items, total


def _filter_products(*, q: str | None = None) -> list[Product]:
    if q is None:
        return PRODUCTS.copy()

    needle = q.casefold()
    return [
        product
        for product in PRODUCTS
        if needle in product.name.casefold() or needle in product.category.casefold()
    ]
