import { useEffect, useMemo, useState } from 'react'
import { loadIndex, loadKpiHistory, loadRun } from './lib/data'
import type { Kpis, RunBundle, RunIndexEntry } from './lib/types'
import RunsView from './views/Runs'
import RunView from './views/Run'
import TraceView from './views/Trace'
import AuditView from './views/Audit'
import KpisView from './views/Kpis'
import GateView from './views/Gate'

const TABS = ['runs', 'run', 'trace', 'audit', 'kpis', 'gate'] as const
type Tab = (typeof TABS)[number]
const LABELS: Record<Tab, string> = { runs: 'Runs', run: 'Run view', trace: 'Trace', audit: 'Audit log', kpis: 'KPIs', gate: 'Gate decision' }

function parseHash(): { tab: Tab; run?: string } {
  const [t, r] = location.hash.replace(/^#\/?/, '').split('/')
  return { tab: (TABS as readonly string[]).includes(t) ? (t as Tab) : 'runs', run: r ? decodeURIComponent(r) : undefined }
}

export default function App() {
  const [index, setIndex] = useState<RunIndexEntry[] | null>(null)
  const [history, setHistory] = useState<Kpis[]>([])
  const [bundle, setBundle] = useState<RunBundle | null>(null)
  const [route, setRoute] = useState(parseHash())
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    const on = () => setRoute(parseHash())
    window.addEventListener('hashchange', on)
    return () => window.removeEventListener('hashchange', on)
  }, [])
  useEffect(() => { loadIndex().then(setIndex).catch((e) => setErr(String(e))); loadKpiHistory().then(setHistory).catch(() => setHistory([])) }, [])
  const selected = useMemo(() => index?.find((e) => e.run_id === route.run) ?? index?.[0], [index, route.run])
  useEffect(() => {
    if (!selected) return
    if (bundle?.entry.run_id === selected.run_id) return
    loadRun(selected).then(setBundle).catch((e) => setErr(String(e)))
  }, [selected, bundle])

  const go = (tab: Tab, run?: string) => { location.hash = `#/${tab}${run ? '/' + encodeURIComponent(run) : route.run ? '/' + encodeURIComponent(route.run) : ''}` }

  return (
    <>
      <header className="top">
        <div><h1>Agentic SDLC — run console</h1><div className="sub">Read-only view over the append-only audit log. Humans decide at gates; agents never merge.</div></div>
        <nav className="tabs" role="tablist">
          {TABS.map((t) => (
            <button key={t} role="tab" aria-selected={route.tab === t} data-testid={`tab-${t}`} onClick={() => go(t)}>{LABELS[t]}</button>
          ))}
        </nav>
        <div className="grow" />
        {bundle && <span className="small muted" data-testid="current-run">run: <b>{bundle.entry.run_id}</b></span>}
      </header>
      <main>
        {err && <div className="panel error">Failed to load run data: {err}</div>}
        {index && index.length === 0 && <div className="panel empty">No runs exported yet. Run <code>harness export</code> then <code>npm run sync-runs</code>.</div>}
        {route.tab === 'runs' && index && <RunsView index={index} onOpen={(id) => go('run', id)} />}
        {route.tab === 'run' && bundle && <RunView b={bundle} />}
        {route.tab === 'trace' && bundle && <TraceView b={bundle} />}
        {route.tab === 'audit' && bundle && <AuditView b={bundle} />}
        {route.tab === 'kpis' && bundle && <KpisView b={bundle} history={history} />}
        {route.tab === 'gate' && bundle && <GateView b={bundle} />}
        {route.tab !== 'runs' && !bundle && index && index.length > 0 && <div className="panel muted">Loading run…</div>}
      </main>
    </>
  )
}
