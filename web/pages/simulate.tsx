import { useEffect, useRef, useState } from "react";
import Layout from "@/components/Layout";
import {
  sendTurn,
  startSession,
  type ConversationTurn,
  type SessionState,
} from "@/lib/api";
import { useRouter } from "next/router";

const SCENARIO_FILES: Record<string, string> = {
  first_visit_new_diagnosis: "personas/first_visit_new_diagnosis.yaml",
  young_professional_hypertension_followup:
    "personas/young_professional_hypertension_followup.yaml",
};

export default function Simulate() {
  const router = useRouter();
  const scenarioId = (router.query.scenario as string) || "first_visit_new_diagnosis";

  const [session, setSession] = useState<SessionState | null>(null);
  const [turns, setTurns] = useState<ConversationTurn[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [started, setStarted] = useState(false);

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight);
  }, [turns]);

  async function begin() {
    setStarted(true);
    setBusy(true);
    setError(null);
    try {
      const path = SCENARIO_FILES[scenarioId] || SCENARIO_FILES.first_visit_new_diagnosis;
      const data = await startSession({ scenario_path: path });
      setSession(data.state);
      setTurns([]);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    if (router.isReady && !started) begin();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router.isReady]);

  async function submit() {
    if (!input.trim() || !session || busy) return;
    const msg = input.trim();
    setInput("");
    setBusy(true);
    setError(null);
    const optimistic: ConversationTurn = { student: msg, patient: null };
    setTurns((t) => [...t, optimistic]);
    try {
      const result = await sendTurn(session.session_id, msg);
      setSession(result);
      const pt = result.current_patient_turn;
      setTurns((t) => {
        const copy = [...t];
        copy[copy.length - 1] = {
          student: msg,
          patient: pt?.patient_utterance || "(no response)",
          emotional_state: pt?.emotional_state,
          flags: pt?.flags,
        };
        return copy;
      });
    } catch (e) {
      setTurns((t) => {
        const copy = [...t];
        copy[copy.length - 1] = { student: msg, patient: "⚠ Error contacting patient model." };
        return copy;
      });
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  if (!session) {
    return (
      <Layout>
        <div className="card p-8 text-center text-slate-500">Loading session…</div>
      </Layout>
    );
  }

  const ended =
    session.is_red_line || session.turn_number >= session.max_turns;

  return (
    <Layout>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">
            {session.persona_id}
          </h1>
          <p className="text-sm text-slate-500">
            Turn {session.turn_number}/{session.max_turns} · {session.difficulty}
          </p>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
          Mood: {session.emotional_state || "—"}
        </span>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      <div
        ref={scrollRef}
        className="card h-[55vh] overflow-y-auto p-4 space-y-4"
      >
        {turns.length === 0 && (
          <p className="text-sm text-slate-400">
            Conversation started. Ask the patient how they are doing.
          </p>
        )}
        {turns.map((t, i) => (
          <div key={i} className="space-y-2">
            <div className="flex justify-end">
              <div className="max-w-[75%] rounded-2xl rounded-br-sm bg-indigo-600 px-4 py-2 text-sm text-white">
                {t.student}
              </div>
            </div>
            {t.patient && (
              <div className="flex justify-start">
                <div className="max-w-[75%] rounded-2xl rounded-bl-sm bg-slate-100 px-4 py-2 text-sm text-slate-800">
                  {t.patient}
                  {t.emotional_state && (
                    <div className="mt-1 text-xs text-slate-500">
                      emotional state: {t.emotional_state}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
        {busy && (
          <div className="flex justify-start">
            <div className="rounded-2xl bg-slate-100 px-4 py-2 text-sm text-slate-400">
              patient is typing…
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          disabled={busy || ended}
          placeholder={
            ended ? "Session ended." : "Type your response to the patient…"
          }
          className="flex-1 rounded-lg border border-slate-300 px-4 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:bg-slate-50"
        />
        <button
          onClick={submit}
          disabled={busy || ended}
          className="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          Send
        </button>
      </div>

      {ended && (
        <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {session.is_red_line
            ? "Session ended: a safety red-line was triggered."
            : "Session ended: maximum turns reached."}{" "}
          <button
            onClick={() => router.reload()}
            className="ml-2 underline underline-offset-2"
          >
            Start a new session
          </button>
        </div>
      )}
    </Layout>
  );
}
