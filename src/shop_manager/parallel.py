"""Threading, multiprocessing and race-condition demonstrations."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path
from threading import Lock, Thread

from shop_manager.analytics import expensive_score
from shop_manager.models import Product

# ---------------------------------------------------------------------------
# ThreadPoolExecutor – I/O-bound style (file loading) and CPU experiments
# ---------------------------------------------------------------------------

def calculate_scores_threads(
    prices: list[float],
    workers: int = 4,
) -> list[float]:
    """Apply expensive_score using ThreadPoolExecutor (CPU-bound, GIL limited)."""
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(expensive_score, prices))


def load_file(path: Path) -> str:
    """Simple I/O worker: read a text file."""
    return path.read_text(encoding="utf-8")


def load_files_parallel(paths: list[Path], workers: int = 8) -> list[str]:
    """I/O-bound parallel file loading with ThreadPoolExecutor."""
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(load_file, paths))


def load_files_sequential(paths: list[Path]) -> list[str]:
    """Sequential file loading for comparison."""
    return [load_file(p) for p in paths]


# ---------------------------------------------------------------------------
# ProcessPoolExecutor – real parallelism for CPU-bound work
# ---------------------------------------------------------------------------

def calculate_scores_processes(
    prices: list[float],
    workers: int = 4,
) -> list[float]:
    """Apply expensive_score using ProcessPoolExecutor."""
    with ProcessPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(expensive_score, prices, chunksize=max(1, len(prices) // (workers * 4))))


# ---------------------------------------------------------------------------
# Race condition demo + Lock fix (concurrent quantity updates)
# ---------------------------------------------------------------------------

class StockCounter:
    """In-memory shared stock quantity with optional synchronization."""

    def __init__(self, initial: int = 0, use_lock: bool = True) -> None:
        self.quantity = initial
        self._lock = Lock()
        self.use_lock = use_lock

    def update(self, delta: int) -> None:
        """Change quantity by delta (positive = restock, negative = sale)."""
        if self.use_lock:
            with self._lock:
                self.quantity += delta
        else:
            # Intentionally unprotected – can produce race conditions
            self.quantity += delta


def run_concurrent_updates(
    counter: StockCounter,
    deltas: list[int],
    workers: int = 8,
) -> int:
    """Launch many threads that concurrently update the shared counter."""
    def worker(delta: int) -> None:
        counter.update(delta)

    threads: list[Thread] = []
    for d in deltas:
        t = Thread(target=worker, args=(d,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return counter.quantity


def demonstrate_race_condition(num_updates: int = 5000) -> tuple[int, int]:
    """Show incorrect result without Lock and correct result with Lock.

    Returns (result_without_lock, result_with_lock).
    Expected correct final value is 0 when half +1 and half -1.
    """
    deltas = [1] * (num_updates // 2) + [-1] * (num_updates // 2)

    # Without lock – race condition may produce non-zero result
    counter_no_lock = StockCounter(initial=0, use_lock=False)
    result_no_lock = run_concurrent_updates(counter_no_lock, deltas, workers=16)

    # With lock – always correct
    counter_lock = StockCounter(initial=0, use_lock=True)
    result_with_lock = run_concurrent_updates(counter_lock, deltas, workers=16)

    return result_no_lock, result_with_lock
