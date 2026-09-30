"""Simple threading example demonstrating concurrent task execution.

This module shows how to create and run multiple threads that execute
independently. Key concepts covered:
  - Custom thread class inheriting from threading.Thread
  - Thread lifecycle: start() and join()
  - Concurrent execution with coordinated timing

Run with: python3 1_basic_threading.py
"""

import logging
import threading
import time

# Configure logging for clearer thread output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-12s] %(message)s",
    datefmt="%H:%M:%S",
)


class MyThread(threading.Thread):
    """Custom thread class that inherits from threading.Thread.

    Each thread instance takes a thread ID, name, counter, and optional delay.
    """

    def __init__(
        self, thread_id: int, name: str, counter: int, delay: float = 0.5
    ) -> None:
        """Initialize the thread with ID, name, counter, and delay.

        Args:
            thread_id: Unique identifier for the thread
            name: Display name for the thread (used in logging)
            counter: Number of iterations to run
            delay: Delay between iterations in seconds
        """
        super().__init__(name=name)
        self.thread_id = thread_id
        self.name = name
        self.counter = counter
        self.delay = delay

    def run(self) -> None:
        """Execute the thread: log start, run iterations, then log end."""
        logging.info(f"Starting thread execution (iterations={self.counter})")
        print_time(self.name, self.counter, self.delay)
        logging.info("Thread execution complete")


def print_time(thread_name: str, counter: int, delay: float) -> None:
    """Log the thread name and current time every 'delay' seconds.

    Args:
        thread_name: Name of the thread (used in logging)
        counter: Number of iterations to run
        delay: Seconds to wait between iterations
    """
    while counter:
        time.sleep(delay)
        logging.info(f"{thread_name}: {time.ctime()} (iterations_left={counter})")
        counter -= 1


def main(delay: float = 0.5) -> None:
    """Create, start, and join worker threads."""
    logging.info("=== Threading example starting ===")

    # Create two threads with different iteration counts
    t1 = MyThread(1, "Thread-1", 1, delay=delay)
    t2 = MyThread(2, "Thread-2", 2, delay=delay)

    # Start the threads (they execute concurrently)
    t1.start()
    t2.start()

    # Wait for both threads to complete before exiting main
    t1.join()
    t2.join()

    logging.info("=== All threads finished ===")


if __name__ == "__main__":
    main()
