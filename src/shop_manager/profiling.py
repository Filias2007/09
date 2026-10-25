"""cProfile and tracemalloc helpers for the shop manager project."""

from __future__ import annotations

import cProfile
import pstats
import tracemalloc
from io import StringIO

from shop_manager.analytics import (
    generate_products,
    price_statistics_python,
    total_stock_value_python,
)


def run_cprofile(count: int = 100_000) -> str:
    """Profile baseline analytics and return a text report."""
    products = generate_products(count)
    prices = [p.price for p in products]

    profiler = cProfile.Profile()
    profiler.enable()

    total_stock_value_python(products)
    price_statistics_python(prices)

    profiler.disable()

    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumulative")
    stats.print_stats(20)
    return stream.getvalue()


def run_tracemalloc(count: int = 100_000) -> dict[str, float]:
    """Measure current and peak memory for generating and processing products."""
    tracemalloc.start()

    products = generate_products(count)
    _ = total_stock_value_python(products)
    prices = [p.price for p in products]
    _ = price_statistics_python(prices)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "current_mb": current / (1024 * 1024),
        "peak_mb": peak / (1024 * 1024),
        "product_count": count,
    }


def memory_snapshot(count: int = 50_000) -> list[str]:
    """Return top memory-consuming lines (for report)."""
    tracemalloc.start()
    products = generate_products(count)
    _ = total_stock_value_python(products)
    snapshot = tracemalloc.take_snapshot()
    tracemalloc.stop()

    stats = snapshot.statistics("lineno")
    return [str(s) for s in stats[:10]]
