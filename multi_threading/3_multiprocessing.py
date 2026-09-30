"""Multiprocessing example demonstrating CPU-bound parallel execution.

This module shows how to use Python's multiprocessing library to run tasks
in parallel across multiple CPU cores. Key concepts covered:
  - Process creation and lifecycle (start, join)
  - Separate memory spaces for true parallelism (bypasses Python's GIL)
  - Passing arguments to target functions in separate processes
  - Using 'if __name__ == "__main__"' guard

Run with: python3 3_multiprocessing.py
"""

import logging
import multiprocessing
import time

# Configure logging for process-safe output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(processName)-14s] %(message)s",
    datefmt="%H:%M:%S",
)


def worker_task(process_name: str, delay: float, iterations: int) -> None:
    """Execute a task in a separate process.

    This function runs in a separate process with its own memory space.
    Each process is independent and can run on a different CPU core.

    Args:
        process_name: Name of the process (used in logging)
        delay: Seconds to wait between iterations
        iterations: Number of times to log the timestamp
    """
    logging.info(f"Starting worker task with {iterations} iterations")

    for remaining in range(iterations, 0, -1):
        time.sleep(delay)
        logging.info(
            f"{process_name}: Timestamp={time.ctime()}, iterations_left={remaining}"
        )

    logging.info("Worker task complete")


def main(delay: float = 0.5, iterations: int = 2) -> None:
    """Create and execute multiple processes in parallel."""
    logging.info("=== Multiprocessing example starting ===")
    logging.info(
        "Key difference from threading: each process has separate memory space"
    )

    processes = [
        multiprocessing.Process(
            target=worker_task, args=("Process-1", delay, iterations), name="Worker-1"
        ),
        multiprocessing.Process(
            target=worker_task, args=("Process-2", delay, iterations), name="Worker-2"
        ),
    ]

    for process in processes:
        logging.info(f"Starting {process.name}")
        process.start()

    for process in processes:
        process.join()
        logging.info(f"{process.name} finished")

    logging.info("=== All processes finished ===")


if __name__ == "__main__":
    main()
