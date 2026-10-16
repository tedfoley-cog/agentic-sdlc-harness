import { useMemo, useState } from 'react'
import type { Kpis, RunBundle } from '../lib/types'
import { Badge, pct } from '../lib/ui'

const METRICS: { key: keyof Kpis; label: string; fmt: (v: unknown) => string }[] = [
  { key: 'autonomy', label: 'Autonomy (agent stages / all stages)', fmt: (v) => pct(v as number) },
  { key: 'first_pass_rate', label: 'First-pass approval', fmt: (v) => pct(v as number) },
  { key: 'loop_resolution_rate', label: 'Loop resolution rate', fmt: (v) => pct(v as number | null) },
  { key: 'requirement_test_coverage', label: 'Requirement test coverage', fmt: (v) => pct(v as number) },
  { key: 'human_review_hours', label: 'Human review hours', fmt: (v) => `${Number(v).toFixed(2)} h` },
  { key: 'cycle_time_minutes', label: 'Cycle time', fmt: (v) => (v == null ? '—' : `${Math.round(Number(v))} min`) },
  { key: 'inference_cost_per_story_point', label: 'Inference cost / story point', fmt: (v) => (v == null ? '—' : `$${Number(v).toFixed(2)}`) },
  { key: 'acus', label: 'ACUs consumed', fmt: (v) => Number(v).toFixed(2) },
]

function Sparkline({ values }: { values: (number | null)[] }) {
  const pts = values.map((v, i) => [i, v ?? 0] as const)
  const max = Math.max(1e-9, ...pts.map((p) => p[1]))
  const w = 520, h = 120, pad = 10
  const x = (i: number) => pad + (i * (w - 2 * pad)) / Math.max(1, pts.length - 1)
  const y = (v: number) => h - pad - (v / max) * (h - 2 * pad)
  return (<svg width={w} height={h} data-testid="kpi-trend-svg" role="img" aria-label="KPI trend">
    <polyline fill="none" stroke="#1f4e79" strokeWidth={2} points={pts.map((p) => `${x(p[0])},${y(p[1])}`).join(' ')} />
    {pts.map((p) => <circle key={p[0]} cx={x(p[0])} cy={y(p[1])} r={3} fill="#1f4e79" />)}
  </svg>)
}

export default function KpisView({ b, history }: { b: RunBundle; history: Kpis[] }) {
  const [metric, setMetric] = useState<keyof Kpis>('autonomy')
  const [scope, setScope] = useState<'all' | 'feature' | 'rca'>('all')
  const k = b.kpis
  const series = useMemo(() => history.filter((h) => scope === 'all' || h.workflow === scope), [history, scope])
  const m = METRICS.find((x) => x.key === metric)!
  return (
    <>
      <div className="panel">
        <h3 style={{ marginTop: 0 }}>Per-run KPIs — {b.entry.run_id}</h3>
        {!k ? <p className="muted">KPIs are computed when the run finishes or pauses at a gate.</p> : (
          <div className="cards">{METRICS.map((mm) => <div className="card" key={mm.key} data-testid={`kpi-card-${mm.key}`}><div className="label">{mm.label}</div><div className="value">{mm.fmt(k[mm.key])}</div></div>)}</div>)}
        {k && (<div className="row" style={{ marginTop: 14 }}>
          <div className="grow"><h4>First-pass by stage</h4><div className="row">{Object.entries(k.first_pass_approval).map(([s, ok]) => <span key={s}><Badge v={ok ? 'PASS' : 'FAIL'} /> <span className="small">{s}</span></span>)}</div></div>
          <div className="grow"><h4>Loop iterations</h4><div className="row">{Object.entries(k.loop_iterations).map(([l, n]) => <span key={l} className="small"><b>{n}</b> {l}</span>)}{Object.keys(k.loop_iterations).length === 0 && <span className="muted small">none</span>}</div></div>
          <div className="grow"><h4>Gate decisions</h4><table><tbody>{k.gates.map((g) => <tr key={g.gate}><td>{g.gate}</td><td><Badge v={g.decision ?? g.status} /></td><td><b>{g.actor ?? '—'}</b></td><td className="small">{g.minutes == null ? '—' : `${g.minutes} min`}</td></tr>)}</tbody></table></div>
        </div>)}
      </div>
      <div className="panel">
        <div className="toolbar"><h3 style={{ margin: 0 }}>Trend over runs</h3>
          <select data-testid="trend-metric" value={metric} onChange={(e) => setMetric(e.target.value as keyof Kpis)}>{METRICS.map((mm) => <option key={mm.key} value={mm.key}>{mm.label}</option>)}</select>
          <select data-testid="trend-scope" value={scope} onChange={(e) => setScope(e.target.value as never)}><option value="all">all workflows</option><option value="feature">feature</option><option value="rca">rca</option></select>
          <span className="muted small" data-testid="trend-count">{series.length} run(s)</span></div>
        {series.length === 0 ? <p className="muted">No history yet.</p> : (<>
          <Sparkline values={series.map((h) => (h[metric] as number | null))} />
          <table data-testid="trend-table"><thead><tr><th>Run</th><th>Workflow</th><th>Status</th><th>{m.label}</th><th>Computed</th></tr></thead>
            <tbody>{series.map((h, i) => <tr key={i}><td className="mono">{h.run_id}</td><td>{h.workflow}</td><td><Badge v={h.status} /></td><td data-testid="trend-value">{m.fmt(h[metric])}</td><td className="small muted">{h.computed_at}</td></tr>)}</tbody></table></>)}
      </div>
    </>
  )
}
