"""Business logic for the online shop."""

from __future__ import annotations

from shop_manager.models import Product


def add_product(products: list[Product], product: Product) -> None:
    """Add a product to the catalog."""
    products.append(product)


def find_by_name(products: list[Product], name: str) -> list[Product]:
    """Search products by name (case-insensitive substring)."""
    name_lower = name.lower()
    return [p for p in products if name_lower in p.name.lower()]


def filter_by_category(products: list[Product], category: str) -> list[Product]:
    """Filter products by exact category name."""
    return [p for p in products if p.category == category]


def most_expensive(products: list[Product]) -> Product | None:
    """Return the product with the highest price."""
    if not products:
        return None
    return max(products, key=lambda p: p.price)


def total_stock_value(products: list[Product]) -> float:
    """Calculate total value of all stock (price * quantity)."""
    return sum(p.price * p.quantity for p in products)


def sort_by_price(products: list[Product], reverse: bool = True) -> list[Product]:
    """Return products sorted by price."""
    return sorted(products, key=lambda p: p.price, reverse=reverse)
