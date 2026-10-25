"""Data model for online shop products."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Product:
    """Product in the online store catalog.

    Attributes:
        name: Product name.
        category: Product category (e.g. Electronics, Books).
        price: Unit price in UAH.
        quantity: Available stock quantity.
    """

    name: str
    category: str
    price: float
    quantity: int

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Product name must not be empty")
        if not self.category or not self.category.strip():
            raise ValueError("Category must not be empty")
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative")

    @property
    def stock_value(self) -> float:
        """Total value of this product in stock."""
        return self.price * self.quantity

    def __repr__(self) -> str:
        return (
            f"Product(name={self.name!r}, category={self.category!r}, "
            f"price={self.price:.2f}, quantity={self.quantity})"
        )
