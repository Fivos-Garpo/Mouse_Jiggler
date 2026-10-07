"""Small Windows-specific helpers used by the jiggler."""

import ctypes
import sys

_ES_CONTINUOUS = 0x80000000
_ES_SYSTEM_REQUIRED = 0x00000001
_ES_DISPLAY_REQUIRED = 0x00000002


def keep_awake() -> None:
    if sys.platform == "win32":
        ctypes.windll.kernel32.SetThreadExecutionState(
            _ES_CONTINUOUS | _ES_SYSTEM_REQUIRED | _ES_DISPLAY_REQUIRED
        )


def restore_power_state() -> None:
    if sys.platform == "win32":
        ctypes.windll.kernel32.SetThreadExecutionState(_ES_CONTINUOUS)
