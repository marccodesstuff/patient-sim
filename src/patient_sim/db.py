from __future__ import annotations

import json
from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    Integer,
    String,
    Text,
    create_engine,
    select,
)
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.orm import declarative_base, sessionmaker

from patient_sim.config.settings import get_settings

Base = declarative_base()


class SessionRow(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    scenario_id = Column(String(255), nullable=False)
    persona_id = Column(String(255), nullable=False)
    difficulty = Column(String(64), nullable=False, default="")
    max_turns = Column(Integer, nullable=False, default=12)
    status = Column(String(32), nullable=False, default="active")
    state = Column(JSON, nullable=False)
    latest_state = Column(JSON, nullable=True)


class TurnRow(Base):
    __tablename__ = "turns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), index=True, nullable=False)
    turn_number = Column(Integer, nullable=False, default=0)
    event = Column(String(64), nullable=False, default="turn")
    payload = Column(JSON, nullable=False)
    raw = Column(Text, nullable=True)


class Database:
    def __init__(self, url: str | None = None, echo: bool = False) -> None:
        self._url = url or get_settings().database_url
        self._engine = create_engine(self._url, echo=echo, future=True)
        self._maker = sessionmaker(bind=self._engine, expire_on_commit=False)
        self._ensured = False

    def ensure_schema(self) -> None:
        if self._ensured:
            return
        Base.metadata.create_all(self._engine)
        self._ensured = True

    def _connect(self) -> DBSession:
        self.ensure_schema()
        return self._maker()

    def create_session(self, session_id: str, state: dict[str, Any]) -> None:
        with self._connect() as db:
            row = SessionRow(
                session_id=session_id,
                scenario_id=state.get("scenario_id", ""),
                persona_id=state.get("persona_id", ""),
                difficulty=state.get("difficulty", ""),
                max_turns=int(state.get("max_turns", 12)),
                status="active",
                state=state,
                latest_state=state,
            )
            db.add(row)
            db.commit()

    def update_session(self, session_id: str, state: dict[str, Any]) -> None:
        with self._connect() as db:
            row = db.execute(
                select(SessionRow).where(SessionRow.session_id == session_id)
            ).scalar_one_or_none()
            if row is None:
                self.create_session(session_id, state)
                return
            row.latest_state = state
            row.state = state
            if bool(state.get("is_red_line")) or int(state.get("turn_number", 0)) >= int(
                state.get("max_turns", 0)
            ):
                row.status = "ended"
            db.commit()

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute(
                select(SessionRow).where(SessionRow.session_id == session_id)
            ).scalar_one_or_none()
            if row is None:
                return None
            return dict(row.latest_state or row.state or {})

    def append_turn(
        self,
        session_id: str,
        turn_number: int,
        payload: dict[str, Any],
        event: str = "turn",
    ) -> None:
        with self._connect() as db:
            db.add(
                TurnRow(
                    session_id=session_id,
                    turn_number=turn_number,
                    event=event,
                    payload=payload,
                    raw=json.dumps(payload, ensure_ascii=False, default=str),
                )
            )
            db.commit()

    def replay(self, session_id: str) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute(
                select(TurnRow)
                .where(TurnRow.session_id == session_id)
                .order_by(TurnRow.id.asc())
            ).scalars().all()
            return [dict(r.payload) for r in rows]
