from __future__ import annotations

import os
import uuid

from patient_sim.db import Database


def _db_url() -> str:
    return os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://postgres@localhost:5432/patient_sim",
    )


def test_db_session_roundtrip():
    db = Database(url=_db_url())
    db.ensure_schema()
    sid = f"test-{uuid.uuid4().hex}"

    state = {"session_id": sid, "scenario_id": "s1", "persona_id": "p1",
             "difficulty": "distressed", "max_turns": 5, "turn_number": 0}
    db.create_session(sid, state)

    got = db.get_session(sid)
    assert got is not None
    assert got["session_id"] == sid
    assert got["scenario_id"] == "s1"

    state["turn_number"] = 1
    db.update_session(sid, state)
    got2 = db.get_session(sid)
    assert got2["turn_number"] == 1

    db.append_turn(sid, 1, {"event": "turn", "foo": "bar"})
    events = db.replay(sid)
    assert len(events) == 1
    assert events[0]["foo"] == "bar"


def test_db_session_missing_returns_none():
    db = Database(url=_db_url())
    db.ensure_schema()
    assert db.get_session(f"nope-{uuid.uuid4().hex}") is None
