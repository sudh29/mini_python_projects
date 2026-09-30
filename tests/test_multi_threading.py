"""Unit tests for multi-threading, multiprocessing, and asyncio concurrency modules."""

import asyncio
import importlib.util
import multiprocessing
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _import_module_from_file(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_basic_threading_execution():
    """Verify thread creation, execution, and join lifecycle."""
    mod = _import_module_from_file(
        "basic_threading", ROOT / "multi_threading" / "1_basic_threading.py"
    )

    t1 = mod.MyThread(1, "Test-1", counter=2, delay=0.01)
    t2 = mod.MyThread(2, "Test-2", counter=2, delay=0.01)

    t1.start()
    t2.start()

    t1.join(timeout=2.0)
    t2.join(timeout=2.0)

    assert not t1.is_alive()
    assert not t2.is_alive()


def test_lock_threading_synchronization():
    """Verify thread locks enforce serial access without deadlocks."""
    mod = _import_module_from_file(
        "lock_threading", ROOT / "multi_threading" / "2_lock_threading.py"
    )

    shared_resource = []

    def critical_task(name: str):
        with mod.thread_lock:
            shared_resource.append(f"{name}_start")
            shared_resource.append(f"{name}_end")

    threads = [
        threading.Thread(target=critical_task, args=(f"T{i}",)) for i in range(5)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=2.0)

    assert len(shared_resource) == 10
    # Verify that starts and ends are paired consecutively without interweaving
    for i in range(0, 10, 2):
        start_tag = shared_resource[i]
        end_tag = shared_resource[i + 1]
        name = start_tag.replace("_start", "")
        assert end_tag == f"{name}_end"


def test_multiprocessing_worker():
    """Verify process creation and execution across process boundaries."""
    mod = _import_module_from_file(
        "mp_demo", ROOT / "multi_threading" / "3_multiprocessing.py"
    )

    proc = multiprocessing.Process(
        target=mod.worker_task,
        args=("TestProcess", 0.01, 2),
    )
    proc.start()
    proc.join(timeout=5.0)

    assert proc.exitcode == 0


def test_asyncio_coroutine_execution():
    """Verify asyncio coroutines execute concurrently via event loop."""
    mod = _import_module_from_file(
        "asyncio_demo", ROOT / "multi_threading" / "4_asyncio.py"
    )

    async def run_test():
        results = await mod.main(delay_scale=0.01)
        return results

    results = asyncio.run(run_test())
    assert len(results) == 3
    assert results[0] == [3, 2, 1]
    assert results[1] == [2, 1]
    assert results[2] == [3, 2, 1]
