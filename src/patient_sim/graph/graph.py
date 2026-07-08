from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from patient_sim.graph.state import ConversationState
from patient_sim.graph.nodes import (
    input_guard,
    retrieve,
    respond,
    parse_structured,
    update_state,
    evaluate_turn,
    log_turn,
)

logger = logging.getLogger(__name__)


def _route_after_log(state: ConversationState) -> str:
    turn_number = int(state.get("turn_number", 0))
    max_turns = int(state.get("max_turns", 12))
    if state.get("is_red_line") or state.get("next") == "end_session":
        return "end_session"
    if turn_number >= max_turns:
        return "end_session"
    return "continue"


def build_graph(checkpointer: Any | None = None):
    g = StateGraph(ConversationState)
    g.add_node("input_guard", input_guard)
    g.add_node("retrieve", retrieve)
    g.add_node("respond", respond)
    g.add_node("parse_structured", parse_structured)
    g.add_node("update_state", update_state)
    g.add_node("evaluate_turn", evaluate_turn)
    g.add_node("log_turn", log_turn)

    g.set_entry_point("input_guard")
    g.add_edge("input_guard", "retrieve")
    g.add_edge("retrieve", "respond")
    g.add_edge("respond", "parse_structured")
    g.add_edge("parse_structured", "update_state")
    g.add_edge("update_state", "evaluate_turn")
    g.add_edge("evaluate_turn", "log_turn")
    g.add_conditional_edges(
        "log_turn",
        _route_after_log,
        {"continue": "input_guard", "end_session": END},
    )
    compiled = g.compile(checkpointer=checkpointer or MemorySaver())
    return compiled
