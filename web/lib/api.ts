export const API_BASE = "/api";

export type ConversationTurn = {
  student: string | null;
  patient: string | null;
  emotional_state?: string;
  flags?: string[];
};

export type PatientTurn = {
  patient_utterance?: string;
  emotional_state?: string;
  revealed_facts?: string[];
  flags?: string[];
};

export type SessionState = {
  session_id: string;
  scenario_id: string;
  persona_id: string;
  turn_number: number;
  max_turns: number;
  difficulty: string;
  emotional_state?: string;
  current_patient_turn?: PatientTurn | null;
  is_red_line?: boolean;
};

export async function startSession(opts: {
  scenario_path: string;
  persona_path?: string;
  difficulty?: string;
  max_turns?: number;
  seed?: number | null;
}): Promise<{ session_id: string; state: SessionState }> {
  const res = await fetch(`${API_BASE}/sessions/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(opts),
  });
  if (!res.ok) throw new Error(`Start failed: ${res.status}`);
  return res.json();
}

export async function sendTurn(
  sessionId: string,
  studentMessage: string
): Promise<SessionState> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/turn`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_message: studentMessage }),
  });
  if (!res.ok) throw new Error(`Turn failed: ${res.status}`);
  return res.json();
}
