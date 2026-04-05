"""
Sample bot — demonstrates the bot execution contract.

This is a simulated bot that mimics a real RPA workflow
(without requiring Selenium or PyAutoGUI). It:
  1. Accepts runtime parameters
  2. Logs structured messages at each step
  3. Captures "screenshots" (placeholder images)
  4. Handles errors gracefully
  5. Reports final status
"""

import random
import time
from datetime import datetime, timezone
from pathlib import Path


class SampleBot:
    """A demo bot that simulates an RPA workflow."""

    def __init__(self, run_id: str, client_id: str, artifacts_dir: Path):
        self.run_id = run_id
        self.client_id = client_id
        self.artifacts_dir = artifacts_dir
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self._logs: list[dict] = []

    def _log(self, level: str, message: str):
        entry = {
            "level": level,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._logs.append(entry)
        print(f"[{level.upper():8}] {message}")

    def execute(self, parameters: dict | None = None) -> dict:
        """Run the bot simulation."""
        self._log("info", f"Bot started — run_id={self.run_id}")
        params = parameters or {}
        item_count = params.get("item_count", random.randint(10, 50))

        try:
            # Step 1: Initialize
            self._log("info", "Initializing browser session...")
            time.sleep(1)

            # Step 2: Login
            self._log("info", "Logging into target application...")
            time.sleep(0.5)
            self._log("info", "Authentication successful")

            # Step 3: Navigate
            self._log("info", "Navigating to work queue...")
            time.sleep(0.5)
            self._log("info", f"Found {item_count} items to process")

            # Step 4: Process items
            processed = 0
            errors = 0
            for i in range(min(item_count, 10)):  # Cap for simulation
                item_id = f"ITEM-{random.randint(1000, 9999)}"
                self._log("info", f"Processing {item_id} ({i+1}/{item_count})...")
                time.sleep(0.3)

                # Simulate occasional issues
                if random.random() < 0.1:
                    self._log("warning", f"Slow response for {item_id} — retrying...")
                    time.sleep(0.5)

                if random.random() < 0.05:
                    self._log("error", f"Failed to process {item_id} — skipping")
                    errors += 1
                    continue

                processed += 1
                self._log("debug", f"  → Form submitted for {item_id}")

            # Step 5: Capture screenshot
            self._capture_screenshot("final_state")

            # Step 6: Cleanup
            self._log("info", "Closing browser session...")
            time.sleep(0.3)

            summary = {
                "status": "success",
                "items_processed": processed,
                "items_failed": errors,
                "total_items": item_count,
            }
            self._log("info", f"Bot completed: {processed} processed, {errors} errors")
            return summary

        except Exception as e:
            self._log("critical", f"Bot crashed: {e}")
            self._capture_screenshot("error_state")
            raise

    def _capture_screenshot(self, name: str):
        """Capture a placeholder screenshot."""
        filepath = self.artifacts_dir / f"{name}_{int(time.time())}.txt"
        filepath.write_text(
            f"Screenshot placeholder: {name}\n"
            f"Run: {self.run_id}\n"
            f"Time: {datetime.now(timezone.utc).isoformat()}\n"
        )
        self._log("info", f"Screenshot captured: {filepath.name}")

    @property
    def logs(self) -> list[dict]:
        return self._logs


# ── Direct execution (for testing) ──────────────────────────────
if __name__ == "__main__":
    import uuid
    bot = SampleBot(
        run_id=str(uuid.uuid4()),
        client_id="test-client",
        artifacts_dir=Path("./test_artifacts"),
    )
    result = bot.execute()
    print(f"\nResult: {result}")
