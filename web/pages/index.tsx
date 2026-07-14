import Layout from "@/components/Layout";
import Link from "next/link";

const SCENARIOS = [
  {
    id: "first_visit_new_diagnosis",
    title: "Anxious Newly-Diagnosed Diabetic",
    persona: "Maria Gonzalez",
    difficulty: "distressed",
    summary:
      "Practice delivering a new diabetes diagnosis to an anxious patient who fears complications.",
  },
  {
    id: "young_professional_hypertension_followup",
    title: "Hypertension Follow-Up",
    persona: "James Carter",
    difficulty: "cooperative",
    summary:
      "A pragmatic young professional returning for a hypertension med check — wants data, not small talk.",
  },
];

export default function Home() {
  return (
    <Layout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Simulation Dashboard</h1>
        <p className="mt-2 text-slate-600">
          Choose a scenario to practice clinical communication with a synthetic patient.
        </p>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        {SCENARIOS.map((s) => (
          <div key={s.id} className="card p-5">
            <div className="mb-2 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900">{s.title}</h2>
              <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
                {s.difficulty}
              </span>
            </div>
            <p className="text-sm text-slate-500">Patient: {s.persona}</p>
            <p className="mt-2 text-sm text-slate-600">{s.summary}</p>
            <Link
              href={`/simulate?scenario=${s.id}`}
              className="mt-4 inline-block rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
            >
              Start simulation
            </Link>
          </div>
        ))}
      </div>
    </Layout>
  );
}
