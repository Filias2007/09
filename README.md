# Shop Manager – Laboratory Work №9

**Course:** Professional Python  
**Variant:** 3 – Online store (Інтернет-магазин)  
**Topic:** Parallelism, multiprocessing and optimization

## Description

Continuation of the individual project (variant 3).  
The system manages a product catalog (name, category, price, quantity).

This laboratory work adds:

- large synthetic datasets (10k–100k+ products);
- baseline pure-Python analytics;
- profiling with `cProfile` and `tracemalloc`;
- threading / `ThreadPoolExecutor`;
- multiprocessing / `ProcessPoolExecutor`;
- race-condition demonstration and fix with `Lock`;
- NumPy vectorization;
- caching of category statistics with invalidation;
- experimental benchmarks and speedup calculation.

## Project structure

```
LAB_07/
├── pyproject.toml
├── README.md
├── .gitignore
├── src/shop_manager/
│   ├── __init__.py
│   ├── models.py
│   ├── services.py
│   ├── analytics.py
│   ├── parallel.py
│   ├── profiling.py
│   └── main.py
├── tests/
│   ├── test_services.py
│   └── test_parallel.py
├── benchmarks/
│   └── benchmark.py
└── report (docx)
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -e ".[test]"
```

## Run demo

```bash
python -m shop_manager.main
```

## Run tests

```bash
python -m pytest -q
```

## Run benchmarks

```bash
python benchmarks/benchmark.py
```

Results are written to `benchmarks/results/benchmark_results.csv`.

## Profiling

```bash
python -c "from shop_manager.profiling import run_cprofile, run_tracemalloc; print(run_cprofile(50000)); print(run_tracemalloc(50000))"
```

## Key experimental conclusions (see full report)

- Pure-Python stock-value and statistics loops are the main CPU-bound bottlenecks.
- `ThreadPoolExecutor` does **not** speed up pure-Python CPU-bound work because of the GIL.
- `ProcessPoolExecutor` provides real speedup for the heavy `expensive_score` function.
- NumPy vectorization gives the largest speedup for aggregate numeric operations.
- Caching significantly accelerates repeated category-statistics queries; invalidation is required after catalog mutations.
- Concurrent quantity updates without a `Lock` can produce a race condition; the lock guarantees correctness.

## License

Educational project for the course «Professional Python».
