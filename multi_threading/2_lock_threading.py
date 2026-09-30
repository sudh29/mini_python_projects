"""Thread synchronization example using threading.Lock.

This module demonstrates how to use locks to synchronize thread execution and
prevent race conditions when multiple threads access shared resources.
Key concepts covered:
  - threading.Lock creation and acquisition
  - with lock: context manager syntax (automatic acquire/release)
  - Thread synchronization: enforcing sequential execution where needed
  - Difference between concurrent and serialized execution

Run with: python3 2_lock_threading.py
"""

import logging
import threading
import time

# Configure logging for thread-safe output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-14s] %(message)s",
    datefmt="%H:%M:%S",
)

# Global lock object for thread synchronization
thread_lock = threading.Lock()


class MyThread(threading.Thread):
    """Custom worker thread that uses a lock to synchronize execution."""

    def __init__(
        self,
        thread_id: int,
        name: str,
        iterations: int,
        lock_before_work: bool = True,
        delay: float = 0.5,
    ) -> None:
        """Initialize the worker thread.

        Args:
            thread_id: Unique identifier for the thread
            name: Display name for logging
            iterations: Number of iterations to run
            lock_before_work: Whether to hold lock during work or for synchronization
            delay: Delay between iterations in seconds
        """
        super().__init__(name=name)
        self.thread_id = thread_id
        self.iterations = iterations
        self.lock_before_work = lock_before_work
        self.delay = delay

    def run(self) -> None:
        """Execute the worker thread with proper lock synchronization."""
        logging.info(f"Starting task (iterations={self.iterations})")

        if self.lock_before_work:
            # Approach 1: Hold lock during entire critical section
            with thread_lock:
                logging.info("Acquired lock - starting protected work")
                print_time(self.name, self.iterations, self.delay)
                logging.info("Releasing lock - work complete")
        else:
            # Approach 2: Brief lock for synchronization only
            with thread_lock:
                logging.info("Synchronized point reached")

            print_time(self.name, self.iterations, self.delay)

        logging.info("Task execution complete")


def print_time(thread_name: str, counter: int, delay: float) -> None:
    """Log the thread name and current time every 'delay' seconds.

    Args:
        thread_name: Name of the thread (used in logging)
        counter: Number of iterations to run
        delay: Seconds to wait between iterations
    """
    while counter:
        time.sleep(delay)
        logging.info(f"{thread_name}: Timestamp={time.ctime()}")
        counter -= 1


def main(delay: float = 0.5) -> None:
    """Demonstrate thread synchronization with locks."""
    logging.info("=== Lock threading example starting ===")

    # Create two threads that both need access to the protected section
    t1 = MyThread(1, "Payment", 2, lock_before_work=True, delay=delay)
    t2 = MyThread(2, "Sending Mail", 2, lock_before_work=True, delay=delay)

    # Start both threads
    t1.start()
    t2.start()

    # Wait for all threads to complete
    t1.join()
    t2.join()

    logging.info("=== All threads finished ===")


if __name__ == "__main__":
    main()
