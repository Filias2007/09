"""Analytics, data generation, baseline and optimized numeric operations."""

from __future__ import annotations

import math
import random
from functools import lru_cache
from typing import Any

import numpy as np

from shop_manager.models import Product

# Global version counter for cache invalidation
_cache_version: int = 0


def invalidate_cache() -> None:
    """Invalidate all analytics caches after data mutation."""
    global _cache_version
    _cache_version += 1
    category_statistics.cache_clear()
    category_statistics_versioned.cache_clear()


def generate_products(
    count: int,
    seed: int = 42,
    categories: list[str] | None = None,
) -> list[Product]:
    """Generate a large synthetic product catalog for benchmarking."""
    if categories is None:
        categories = [
            "Electronics",
            "Books",
            "Clothing",
            "Home",
            "Sports",
            "Toys",
            "Beauty",
            "Food",
        ]

    random.seed(seed)
    products: list[Product] = []
    for i in range(count):
        cat = categories[i % len(categories)]
        price = round(random.uniform(10.0, 5000.0), 2)
        quantity = random.randint(0, 500)
        products.append(
            Product(
                name=f"Product-{i:06d}",
                category=cat,
                price=price,
                quantity=quantity,
            )
        )
    return products


# ---------------------------------------------------------------------------
# Baseline (pure Python loops) – CPU-bound stock value & statistics
# ---------------------------------------------------------------------------

def total_stock_value_python(products: list[Product]) -> float:
    """Baseline: sum(price * quantity) with pure Python loop."""
    total = 0.0
    for p in products:
        total += p.price * p.quantity
    return total


def category_stats_python(products: list[Product]) -> dict[str, dict[str, float]]:
    """Baseline category statistics with pure Python."""
    stats: dict[str, dict[str, float]] = {}
    for p in products:
        if p.category not in stats:
            stats[p.category] = {
                "count": 0.0,
                "total_value": 0.0,
                "sum_price": 0.0,
                "min_price": float("inf"),
                "max_price": float("-inf"),
            }
        s = stats[p.category]
        s["count"] += 1
        s["total_value"] += p.price * p.quantity
        s["sum_price"] += p.price
        s["min_price"] = min(s["min_price"], p.price)
        s["max_price"] = max(s["max_price"], p.price)

    for cat, s in stats.items():
        count = s["count"]
        s["avg_price"] = s["sum_price"] / count if count else 0.0
        del s["sum_price"]
    return stats


def price_statistics_python(prices: list[float]) -> dict[str, float]:
    """Baseline numeric statistics on a list of prices."""
    if not prices:
        return {"average": 0.0, "minimum": 0.0, "maximum": 0.0, "std": 0.0}
    count = len(prices)
    average = sum(prices) / count
    minimum = min(prices)
    maximum = max(prices)
    variance = sum((v - average) ** 2 for v in prices) / count
    return {
        "average": average,
        "minimum": minimum,
        "maximum": maximum,
        "std": math.sqrt(variance),
    }


def expensive_score(price: float) -> float:
    """CPU-heavy pure-Python function used for parallel experiments.

    Simulates a non-trivial computation on each product price.
    """
    value = price
    for _ in range(50):
        value = (
            math.sin(value) ** 2
            + math.cos(value) ** 2
            + math.sqrt(abs(value) + 1.0)
        )
    return value


def calculate_scores_sequential(prices: list[float]) -> list[float]:
    """Sequential application of expensive_score."""
    return [expensive_score(p) for p in prices]


# ---------------------------------------------------------------------------
# NumPy vectorized implementations
# ---------------------------------------------------------------------------

def total_stock_value_numpy(products: list[Product]) -> float:
    """Vectorized total stock value with NumPy."""
    prices = np.fromiter((p.price for p in products), dtype=np.float64, count=len(products))
    quantities = np.fromiter(
        (p.quantity for p in products), dtype=np.float64, count=len(products)
    )
    return float(np.dot(prices, quantities))


def price_statistics_numpy(prices: list[float]) -> dict[str, float]:
    """Vectorized statistics with NumPy."""
    if not prices:
        return {"average": 0.0, "minimum": 0.0, "maximum": 0.0, "std": 0.0}
    arr = np.asarray(prices, dtype=np.float64)
    return {
        "average": float(arr.mean()),
        "minimum": float(arr.min()),
        "maximum": float(arr.max()),
        "std": float(arr.std()),
    }


def mass_reprice_numpy(products: list[Product], factor: float = 1.1) -> list[float]:
    """Apply a price factor to all products using NumPy (returns new prices)."""
    prices = np.fromiter((p.price for p in products), dtype=np.float64, count=len(products))
    return (prices * factor).tolist()


# ---------------------------------------------------------------------------
# Caching for category statistics
# ---------------------------------------------------------------------------

@lru_cache(maxsize=64)
def category_statistics(category: str, version: int) -> dict[str, float]:
    """Cached category statistics.

    The `version` argument is part of the cache key and is incremented
    by invalidate_cache() after any mutation of the product catalog.
    """
    # This function is a pure wrapper; real data is injected via
    # category_statistics_versioned which holds a reference to products.
    # For the lab we use a module-level products list that callers set.
    return _compute_category_stats(category)


# Module-level reference used by the cached function (set by callers)
_products_ref: list[Product] = []


def set_products_for_cache(products: list[Product]) -> None:
    """Set the product list used by cached category statistics."""
    global _products_ref
    _products_ref = products
    invalidate_cache()


def _compute_category_stats(category: str) -> dict[str, float]:
    """Actual (uncached) computation of category statistics."""
    filtered = [p for p in _products_ref if p.category == category]
    if not filtered:
        return {
            "count": 0.0,
            "total_value": 0.0,
            "avg_price": 0.0,
            "min_price": 0.0,
            "max_price": 0.0,
        }
    count = len(filtered)
    total_value = sum(p.price * p.quantity for p in filtered)
    prices = [p.price for p in filtered]
    return {
        "count": float(count),
        "total_value": total_value,
        "avg_price": sum(prices) / count,
        "min_price": min(prices),
        "max_price": max(prices),
    }


@lru_cache(maxsize=64)
def category_statistics_versioned(category: str, version: int) -> dict[str, float]:
    """Versioned cache entry for category statistics."""
    return _compute_category_stats(category)


def get_category_stats(category: str) -> dict[str, float]:
    """Public API: return cached (or freshly computed) category statistics."""
    return category_statistics_versioned(category, _cache_version)
