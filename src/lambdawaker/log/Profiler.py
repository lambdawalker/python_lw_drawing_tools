import time
from functools import wraps
from typing import Optional, Dict


class Profiler:
    def __init__(self, verbose: bool = False):
        self.active_timers: Dict[str, float] = {}
        self.verbose = verbose
        self._check_counter = 0
        # Use perf_counter for high-precision timing
        self._global_start = time.perf_counter()

    def begin(self, label: str, verbose: Optional[bool] = None):
        """Starts a named timer."""
        is_verbose = verbose if verbose is not None else self.verbose
        if is_verbose:
            print(f"[Profiler] Starting: {label}")

        self.active_timers[label] = time.perf_counter()

    def peek(self, label: str) -> float:
        """Returns elapsed time without stopping the timer."""
        if label not in self.active_timers:
            raise KeyError(f"Timer '{label}' was never started.")
        return time.perf_counter() - self.active_timers[label]

    def stop(self, label: str, verbose: Optional[bool] = None) -> float:
        """Stops the timer and returns total duration."""
        duration = self.peek(label)
        del self.active_timers[label]

        is_verbose = verbose if verbose is not None else self.verbose
        if is_verbose:
            print(f"[Profiler] {label} completed in {duration:.4f}s")
        return duration

    def checkpoint(self, label: Optional[str] = None) -> float:
        """Measures time since the Profiler was initialized (global offset)."""
        self._check_counter += 1
        tag = label or f"Checkpoint {self._check_counter}"
        elapsed = time.perf_counter() - self._global_start

        if self.verbose:
            print(f"[Profiler] {tag}: {elapsed:.4f}s since init")
        return elapsed


def time_it(func):
    """Decorator to measure function execution time."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"DEBUG: '{func.__name__}' took {end - start:.6f}s")
        return result

    return wrapper
