from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from patient_sim.config.settings import get_settings


def configure_logging(settings=None) -> None:
    settings = settings or get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


class TurnLogger:
    def __init__(self, session_id: str, log_dir: str | None = None) -> None:
        self.session_id = session_id
        self.log_dir = Path(log_dir or get_settings().chroma_persist_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._path = self.log_dir / f"{session_id}.jsonl"
        self._start = time.time()

    def log_turn(self, record: dict[str, Any]) -> None:
        record.setdefault("session_id", self.session_id)
        record.setdefault("elapsed_ms", int((time.time() - self._start) * 1000))
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    def path(self) -> Path:
        return self._path
