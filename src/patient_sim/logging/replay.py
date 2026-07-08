from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patient_sim.config.settings import get_settings
from patient_sim.logging.structured_logger import TurnLogger


class SessionReplayer:
    def __init__(self, session_id: str, log_dir: str | None = None) -> None:
        self.session_id = session_id
        self.log_path = Path(log_dir or get_settings().chroma_persist_dir) / f"{session_id}.jsonl"

    def replay(self) -> list[dict[str, Any]]:
        if not self.log_path.exists():
            return []
        out: list[dict[str, Any]] = []
        for line in self.log_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return out
