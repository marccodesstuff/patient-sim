from __future__ import annotations

import os
from typing import Any

from patient_sim.config.settings import get_settings


class LangSmithHook:
    def __init__(self) -> None:
        self.enabled = str(os.getenv("LANGSMITH_TRACING", "false")).lower() in {"1", "true", "yes"}
        self.project = os.getenv("LANGSMITH_PROJECT", "patient-sim")

    def enable(self) -> None:
        if not self.enabled:
            print("[LangSmith] Tracing not enabled; set LANGSMITH_TRACING=true and provide LANGSMITH_API_KEY.")
            return
        try:
            import langsmith  # noqa: F401
            print(f"[LangSmith] Tracing enabled for project={self.project}")
        except Exception as exc:
            print(f"[LangSmith] Could not enable tracing: {exc}")
