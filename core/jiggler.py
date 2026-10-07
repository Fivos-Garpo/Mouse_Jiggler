"""Mouse movement engine with start, pause/resume and stop support."""

from __future__ import annotations

import random
import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional

import pyautogui

from core.windows import keep_awake, restore_power_state


@dataclass(frozen=True)
class JigglerConfig:
    max_delay: float
    duration_minutes: float


class MouseJiggler:
    """Run randomized mouse movements without blocking the GUI thread."""

    def __init__(self, on_status: Optional[Callable[[str], None]] = None) -> None:
        self._on_status = on_status
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()
        self._lock = threading.Lock()
        self._running = False
        self._paused = False
        self._started_at = 0.0
        self._paused_at = 0.0
        self._paused_total = 0.0
        self._config: Optional[JigglerConfig] = None

    @property
    def running(self) -> bool:
        return self._running

    @property
    def paused(self) -> bool:
        return self._paused

    def start(self, config: JigglerConfig) -> bool:
        if config.max_delay <= 0 or config.duration_minutes <= 0:
            raise ValueError("Delay and duration must be greater than zero.")

        with self._lock:
            if self._running:
                return False
            self._config = config
            self._running = True
            self._paused = False
            self._started_at = time.monotonic()
            self._paused_at = 0.0
            self._paused_total = 0.0
            self._stop_event.clear()
            self._pause_event.set()
            self._thread = threading.Thread(target=self._worker, daemon=True, name="MouseJiggler")
            self._thread.start()

        keep_awake()
        self._status("Jiggler started.")
        return True

    def pause(self) -> bool:
        with self._lock:
            if not self._running or self._paused:
                return False
            self._paused = True
            self._paused_at = time.monotonic()
            self._pause_event.clear()
        self._status("Paused.")
        return True

    def resume(self) -> bool:
        with self._lock:
            if not self._running or not self._paused:
                return False
            self._paused_total += time.monotonic() - self._paused_at
            self._paused_at = 0.0
            self._paused = False
            self._pause_event.set()
        self._status("Resumed.")
        return True

    def stop(self) -> bool:
        with self._lock:
            if not self._running:
                return False
            self._stop_event.set()
            self._pause_event.set()
        self._status("Stopping...")
        return True

    def elapsed_seconds(self) -> float:
        if not self._running:
            return 0.0
        paused = self._paused_total
        if self._paused:
            paused += time.monotonic() - self._paused_at
        return max(0.0, time.monotonic() - self._started_at - paused)

    def _worker(self) -> None:
        config = self._config
        if config is None:
            return

        total_seconds = config.duration_minutes * 60.0
        try:
            while not self._stop_event.is_set():
                if self.elapsed_seconds() >= total_seconds:
                    self._status("Finished.")
                    break

                self._pause_event.wait()
                if self._stop_event.is_set():
                    break

                width, height = pyautogui.size()
                x = random.randint(0, max(0, width - 1))
                y = random.randint(0, max(0, height - 1))
                pyautogui.moveTo(x, y, duration=random.uniform(0.2, 1.0))

                delay = random.uniform(0.2, config.max_delay)
                if self._interruptible_sleep(delay):
                    break
        finally:
            restore_power_state()
            with self._lock:
                self._running = False
                self._paused = False
                self._thread = None
            self._status("Stopped." if self._stop_event.is_set() else "Ready.")

    def _interruptible_sleep(self, seconds: float) -> bool:
        deadline = time.monotonic() + seconds
        while not self._stop_event.is_set():
            if not self._pause_event.is_set():
                self._pause_event.wait()
                continue
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            time.sleep(min(0.1, remaining))
        return True

    def _status(self, message: str) -> None:
        if self._on_status:
            self._on_status(message)
