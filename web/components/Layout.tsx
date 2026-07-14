import type { ReactNode } from "react";

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white font-bold">
              P
            </div>
            <span className="text-lg font-semibold text-slate-900">
              PatientSim
            </span>
            <span className="ml-2 rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700">
              Clinical Training
            </span>
          </div>
          <nav className="hidden gap-6 text-sm text-slate-600 md:flex">
            <a className="hover:text-slate-900" href="/">Dashboard</a>
            <a className="hover:text-slate-900" href="/simulate">Simulate</a>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
      <footer className="border-t border-slate-200 py-6 text-center text-xs text-slate-400">
        PatientSim — training simulator only. All personas are synthetic.
      </footer>
    </div>
  );
}
