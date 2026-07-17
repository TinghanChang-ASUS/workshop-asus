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
    products = _filter_products(q=q)

    products.sort(key=lambda product: getattr(product, sort), reverse=order == "desc")

    start = (page - 1) * page_size
    end = start + page_size
    return products[start:end]


def count_products(*, q: str | None = None) -> int:
    return len(_filter_products(q=q))


def get_product(product_id: int) -> Product | None:
    return next((product for product in PRODUCTS if product.id == product_id), None)


def _filter_products(*, q: str | None = None) -> list[Product]:
    if q is None:
        return PRODUCTS.copy()

    needle = q.casefold()
    return [
        product
        for product in PRODUCTS
        if needle in product.name.casefold() or needle in product.category.casefold()
    ]
