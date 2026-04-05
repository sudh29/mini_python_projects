"""
Screenshot utility for bot workers.
Captures screenshots from Selenium WebDriver or PyAutoGUI
and saves them to the artifact storage.
"""

import os
import time
from datetime import datetime, timezone
from pathlib import Path


class ScreenshotCapture:
    """Manages screenshot capture and storage for bot runs."""

    def __init__(self, artifacts_dir: Path):
        self.artifacts_dir = artifacts_dir
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self._counter = 0

    def capture_selenium(self, driver, name: str | None = None) -> str:
        """
        Capture a screenshot from a Selenium WebDriver instance.

        Args:
            driver: Selenium WebDriver instance
            name:   Optional name prefix (default: auto-increment)

        Returns:
            Path to the saved screenshot
        """
        self._counter += 1
        filename = self._make_filename(name)
        filepath = self.artifacts_dir / filename

        try:
            driver.save_screenshot(str(filepath))
            return str(filepath)
        except Exception as e:
            # Fallback: save error info
            error_path = self.artifacts_dir / f"error_{filename}.txt"
            error_path.write_text(f"Screenshot failed: {e}")
            return str(error_path)

    def capture_pyautogui(self, name: str | None = None, region: tuple | None = None) -> str:
        """
        Capture a screenshot using PyAutoGUI (full screen or region).

        Args:
            name:   Optional name prefix
            region: Optional (left, top, width, height) tuple

        Returns:
            Path to the saved screenshot
        """
        try:
            import pyautogui
            self._counter += 1
            filename = self._make_filename(name)
            filepath = self.artifacts_dir / filename

            screenshot = pyautogui.screenshot(region=region)
            screenshot.save(str(filepath))
            return str(filepath)
        except ImportError:
            return self._save_placeholder(name or "pyautogui")
        except Exception as e:
            return self._save_placeholder(f"error_{name or 'screenshot'}")

    def capture_on_error(self, driver=None, name: str = "error") -> str:
        """
        Capture a screenshot on error — tries Selenium first, then PyAutoGUI.
        Always succeeds (saves placeholder on all failures).
        """
        if driver:
            try:
                return self.capture_selenium(driver, name)
            except Exception:
                pass

        try:
            return self.capture_pyautogui(name)
        except Exception:
            return self._save_placeholder(name)

    def _make_filename(self, name: str | None) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        prefix = name or f"step_{self._counter:03d}"
        return f"{prefix}_{timestamp}.png"

    def _save_placeholder(self, name: str) -> str:
        """Save a placeholder text file when screenshot capture fails."""
        self._counter += 1
        filename = f"{name}_{self._counter:03d}_placeholder.txt"
        filepath = self.artifacts_dir / filename
        filepath.write_text(
            f"Screenshot placeholder\n"
            f"Name: {name}\n"
            f"Time: {datetime.now(timezone.utc).isoformat()}\n"
            f"Note: Actual screenshot capture was unavailable\n"
        )
        return str(filepath)
