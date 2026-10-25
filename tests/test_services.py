"""Tests for core business logic."""

from __future__ import annotations

import pytest

from shop_manager.models import Product
from shop_manager.services import (
    add_product,
    filter_by_category,
    find_by_name,
    most_expensive,
    sort_by_price,
    total_stock_value,
)


@pytest.fixture
def sample_products() -> list[Product]:
    return [
        Product("Laptop", "Electronics", 25000.0, 3),
        Product("Book", "Books", 250.0, 10),
        Product("Phone", "Electronics", 12000.0, 5),
        Product("Shirt", "Clothing", 500.0, 20),
    ]


def test_add_product(sample_products: list[Product]) -> None:
    add_product(sample_products, Product("Mouse", "Electronics", 300.0, 15))
    assert len(sample_products) == 5


def test_filter_by_category(sample_products: list[Product]) -> None:
    electronics = filter_by_category(sample_products, "Electronics")
    assert len(electronics) == 2
    assert all(p.category == "Electronics" for p in electronics)


def test_most_expensive(sample_products: list[Product]) -> None:
    best = most_expensive(sample_products)
    assert best is not None
    assert best.name == "Laptop"
    assert best.price == 25000.0


def test_total_stock_value(sample_products: list[Product]) -> None:
    # 25000*3 + 250*10 + 12000*5 + 500*20 = 75000 + 2500 + 60000 + 10000 = 147500
    assert total_stock_value(sample_products) == pytest.approx(147500.0)


def test_sort_by_price(sample_products: list[Product]) -> None:
    sorted_p = sort_by_price(sample_products)
    assert sorted_p[0].name == "Laptop"
    assert sorted_p[-1].name == "Book"


def test_product_validation() -> None:
    with pytest.raises(ValueError):
        Product("", "Electronics", 100.0, 1)
    with pytest.raises(ValueError):
        Product("X", "Electronics", -1.0, 1)
    with pytest.raises(ValueError):
        Product("X", "Electronics", 10.0, -5)
