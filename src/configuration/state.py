from __future__ import annotations

from types import SimpleNamespace
from typing import Any

_app: Any | None = None


def set_current_app(app: Any) -> None:
    global _app
    _app = app


def get_app_state() -> SimpleNamespace:
    if _app is None:
        raise RuntimeError("Application has not been initialised")
    return _app.state
