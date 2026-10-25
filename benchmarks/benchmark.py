"""Main benchmark suite for Lab 09 – Online Shop (variant 3)."""

from __future__ import annotations

import csv
import os
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Callable

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
)


def benchmark_repeated(
    func: Callable,
    *args,
    repeats: int = 5,
    **kwargs,
) -> float:
    """Run function several times and return mean elapsed seconds."""
    times: list[float] = []
    for _ in range(repeats):
        start = perf_counter()
        func(*args, **kwargs)
        times.append(perf_counter() - start)
    return mean(times)


def calculate_speedup(baseline: float, optimized: float) -> float:
    if optimized <= 0:
        return float("inf")
    return baseline / optimized


def run_all_benchmarks(
    sizes: list[int] | None = None,
    workers_list: list[int] | None = None,
    repeats: int = 3,
) -> list[dict]:
    """Execute the full experimental matrix and return rows for CSV/table."""
    if sizes is None:
        sizes = [10_000, 50_000, 100_000]
    if workers_list is None:
        workers_list = [1, 2, 4]

    results: list[dict] = []
    cpu_count = os.cpu_count() or 4
    print(f"CPU count: {cpu_count}")
    print(f"Repeats per measurement: {repeats}")
    print("-" * 70)

    for size in sizes:
        print(f"\n=== Dataset size: {size:,} products ===")
        products = generate_products(size)
        prices = [p.price for p in products]

        # --- Total stock value (Python vs NumPy) ---
        t_py = benchmark_repeated(total_stock_value_python, products, repeats=repeats)
        t_np = benchmark_repeated(total_stock_value_numpy, products, repeats=repeats)
        print(f"  Stock value Python : {t_py:.6f} s")
        print(f"  Stock value NumPy  : {t_np:.6f} s  (speedup {calculate_speedup(t_py, t_np):.2f}x)")

        results.append(
            {
                "experiment": "stock_value",
                "size": size,
                "method": "Python",
                "workers": 1,
                "mean_time": round(t_py, 6),
                "speedup": 1.0,
            }
        )
        results.append(
            {
                "experiment": "stock_value",
                "size": size,
                "method": "NumPy",
                "workers": "-",
                "mean_time": round(t_np, 6),
                "speedup": round(calculate_speedup(t_py, t_np), 2),
            }
        )

        # --- Price statistics (Python vs NumPy) ---
        t_stat_py = benchmark_repeated(price_statistics_python, prices, repeats=repeats)
        t_stat_np = benchmark_repeated(price_statistics_numpy, prices, repeats=repeats)
        print(f"  Stats Python       : {t_stat_py:.6f} s")
        print(f"  Stats NumPy        : {t_stat_np:.6f} s  (speedup {calculate_speedup(t_stat_py, t_stat_np):.2f}x)")

        results.append(
            {
                "experiment": "price_stats",
                "size": size,
                "method": "Python",
                "workers": 1,
                "mean_time": round(t_stat_py, 6),
                "speedup": 1.0,
            }
        )
        results.append(
            {
                "experiment": "price_stats",
                "size": size,
                "method": "NumPy",
                "workers": "-",
                "mean_time": round(t_stat_np, 6),
                "speedup": round(calculate_speedup(t_stat_py, t_stat_np), 2),
            }
        )

        # --- CPU-bound expensive_score (sequential / threads / processes) ---
        # Use a smaller subset for the heavy function to keep total runtime reasonable
        score_size = min(size, 20_000)
        score_prices = prices[:score_size]

        t_seq = benchmark_repeated(
            calculate_scores_sequential, score_prices, repeats=max(1, repeats - 1)
        )
        print(f"  Scores Sequential  : {t_seq:.6f} s  (n={score_size})")

        results.append(
            {
                "experiment": "expensive_score",
                "size": score_size,
                "method": "Sequential",
                "workers": 1,
                "mean_time": round(t_seq, 6),
                "speedup": 1.0,
            }
        )

        for w in workers_list:
            t_thr = benchmark_repeated(
                calculate_scores_threads, score_prices, workers=w, repeats=max(1, repeats - 1)
            )
            t_proc = benchmark_repeated(
                calculate_scores_processes, score_prices, workers=w, repeats=max(1, repeats - 1)
            )
            print(
                f"  Scores Threads  w={w}: {t_thr:.6f} s  "
                f"(speedup {calculate_speedup(t_seq, t_thr):.2f}x)"
            )
            print(
                f"  Scores Process  w={w}: {t_proc:.6f} s  "
                f"(speedup {calculate_speedup(t_seq, t_proc):.2f}x)"
            )

            results.append(
                {
                    "experiment": "expensive_score",
                    "size": score_size,
                    "method": "ThreadPool",
                    "workers": w,
                    "mean_time": round(t_thr, 6),
                    "speedup": round(calculate_speedup(t_seq, t_thr), 2),
                }
            )
            results.append(
                {
                    "experiment": "expensive_score",
                    "size": score_size,
                    "method": "ProcessPool",
                    "workers": w,
                    "mean_time": round(t_proc, 6),
                    "speedup": round(calculate_speedup(t_seq, t_proc), 2),
                }
            )

    return results


def save_results(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["experiment", "size", "method", "workers", "mean_time", "speedup"],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nResults saved to {path}")


def main() -> None:
    # Reasonable sizes for a student machine / CI environment
    rows = run_all_benchmarks(
        sizes=[10_000, 50_000, 100_000],
        workers_list=[1, 2, 4],
        repeats=3,
    )
    out = Path(__file__).resolve().parent / "results" / "benchmark_results.csv"
    save_results(rows, out)

    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY (key rows)")
    print("=" * 70)
    for r in rows:
        if r["method"] in ("Python", "NumPy", "Sequential") or (
            r["method"] in ("ThreadPool", "ProcessPool") and r["workers"] == 4
        ):
            print(
                f"{r['experiment']:16} {r['size']:8} {r['method']:12} "
                f"w={str(r['workers']):3}  {r['mean_time']:10.6f}s  "
                f"speedup={r['speedup']}"
            )


if __name__ == "__main__":
    main()
