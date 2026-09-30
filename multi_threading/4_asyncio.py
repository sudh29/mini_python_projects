"""Asyncio example demonstrating concurrent task execution with async/await.

This module shows how to use Python's asyncio library to run multiple
coroutines concurrently. Key concepts covered:
  - Coroutines and async/await syntax
  - Event loop for managing concurrent execution
  - asyncio.gather() for running tasks concurrently
  - Async I/O operations without threads

Unlike threading, asyncio runs on a single thread using an event loop.
It's ideal for I/O-bound operations like network requests and file operations.

Run with: python3 4_asyncio.py
"""

import asyncio
import logging
import time

# Configure logging for clearer asyncio output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)-15s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("asyncio_demo")


async def worker_task(
    task_id: int, task_name: str, delay: float, iterations: int
) -> list[int]:
    """Execute an async worker task that logs timestamps at regular intervals.

    This coroutine runs concurrently with other coroutines in the event loop.
    The await asyncio.sleep() call yields control to allow other tasks to run.

    Args:
        task_id: Unique identifier for the task
        task_name: Display name for the task (used in logging)
        delay: Seconds to wait between iterations (uses asyncio.sleep)
        iterations: Number of times to log the timestamp

    Returns:
        list[int]: Completed iteration indices
    """
    logger.info(f"Task {task_id} ({task_name}) starting with {iterations} iterations")
    completed = []

    for remaining in range(iterations, 0, -1):
        await asyncio.sleep(delay)
        logger.info(
            f"Task {task_id} ({task_name}): {time.ctime()}, iterations_left={remaining}"
        )
        completed.append(remaining)

    logger.info(f"Task {task_id} ({task_name}) complete")
    return completed


async def main(delay_scale: float = 0.5) -> list[list[int]]:
    """Create and run multiple coroutines concurrently using asyncio."""
    logger.info("=== Asyncio example starting ===")
    logger.info(
        "Key benefit: runs concurrently on single thread without GIL limitations"
    )

    tasks = [
        worker_task(1, "Task-A", delay=1.0 * delay_scale, iterations=3),
        worker_task(2, "Task-B", delay=1.5 * delay_scale, iterations=2),
        worker_task(3, "Task-C", delay=0.8 * delay_scale, iterations=3),
    ]

    start_time = time.time()
    results = await asyncio.gather(*tasks)
    end_time = time.time()

    logger.info(
        f"=== All tasks finished (total time: {end_time - start_time:.2f}s) ==="
    )
    logger.info("Note: Tasks ran concurrently, so total time < sum of all delays")
    return list(results)


if __name__ == "__main__":
    asyncio.run(main())
