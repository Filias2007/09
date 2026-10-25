"""Tests for parallel implementations and correctness of optimizations."""

from __future__ import annotations

import pytest

from shop_manager.analytics import (
    calculate_scores_sequential,
    generate_products,
    price_statistics_numpy,
    price_statistics_python,
    total_stock_value_numpy,
    total_stock_value_python,
)
from shop_manager.parallel import (
    calculate_scores_processes,
    calculate_scores_threads,
    demonstrate_race_condition,
)


@pytest.fixture
def small_products():
    return generate_products(200, seed=99)


def test_stock_value_numpy_matches_python(small_products) -> None:
    py = total_stock_value_python(small_products)
    np_val = total_stock_value_numpy(small_products)
    assert np_val == pytest.approx(py, rel=1e-9)


def test_price_statistics_match(small_products) -> None:
    prices = [p.price for p in small_products]
    py = price_statistics_python(prices)
    np_s = price_statistics_numpy(prices)
    assert np_s["average"] == pytest.approx(py["average"])
    assert np_s["minimum"] == pytest.approx(py["minimum"])
    assert np_s["maximum"] == pytest.approx(py["maximum"])
    assert np_s["std"] == pytest.approx(py["std"], rel=1e-6)


def test_scores_threads_match_sequential() -> None:
    prices = [10.0, 20.5, 33.3, 100.0, 7.7]
    seq = calculate_scores_sequential(prices)
    thr = calculate_scores_threads(prices, workers=2)
    assert thr == pytest.approx(seq)


def test_scores_processes_match_sequential() -> None:
    prices = [10.0, 20.5, 33.3, 100.0, 7.7]
    seq = calculate_scores_sequential(prices)
    proc = calculate_scores_processes(prices, workers=2)
    assert proc == pytest.approx(seq)


def test_race_condition_fixed_by_lock() -> None:
    no_lock, with_lock = demonstrate_race_condition(1000)
    # With lock the result must be exactly 0 (half +1, half -1)
    assert with_lock == 0
    # Without lock we only check that the function runs; race may or may not appear
    # on a given run, so we do not assert inequality.
    assert isinstance(no_lock, int)
