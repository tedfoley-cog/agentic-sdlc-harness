import { useMemo, useState } from 'react'
import type { LogRecord, RunBundle } from '../lib/types'
import { Badge, fmtTs } from '../lib/ui'

const HIDE = new Set(['seq', 'ts', 'event', 'prev', 'hash'])

export default function AuditView({ b }: { b: RunBundle }) {
  const [q, setQ] = useState('')
  const [event, setEvent] = useState('all')
  const [sel, setSel] = useState<LogRecord | null>(null)
  const events = useMemo(() => [...new Set(b.log.map((r) => r.event))].sort(), [b.log])
  const rows = useMemo(() => b.log.filter((r) => (event === 'all' || r.event === event) &&
    (q === '' || JSON.stringify(r).toLowerCase().includes(q.toLowerCase()))), [b.log, q, event])
  const humans = useMemo(() => [...new Set(b.log.filter((r) => r.event === 'gate.decided' || r.event === 'question.answered' || r.event === 'human.time').map((r) => String(r.actor)))], [b.log])
  return (
    <>
      <div className="panel row">
        <span data-testid="chain-badge" className={b.chainOk ? 'ok' : 'error'}><b>{b.chainOk ? 'Append-only chain verified in browser' : 'Chain broken'}</b> — {b.chainMessage}</span>
        <span className="muted small">sha256 over sorted-key JSON of each record incl. <code>prev</code>; re-computed client-side</span>
        <div className="grow" />
        <span className="small">human actors: {humans.length ? humans.map((h) => <b key={h} style={{ marginLeft: 6 }}>{h}</b>) : '—'}</span>
      </div>
      <div className="panel">
        <div className="toolbar">
          <select data-testid="audit-event" value={event} onChange={(e) => setEvent(e.target.value)}><option value="all">All events</option>{events.map((e) => <option key={e}>{e}</option>)}</select>
          <input data-testid="audit-search" placeholder="Search any field…" value={q} onChange={(e) => setQ(e.target.value)} />
          <span className="muted small" data-testid="audit-count">{rows.length} of {b.log.length} records</span>
        </div>
        <table data-testid="audit-table"><thead><tr><th>#</th><th>Time</th><th>Event</th><th>Stage / gate</th><th>Verdict / decision</th><th>Actor / model</th><th>Hash</th></tr></thead>
          <tbody>{rows.map((r) => (<tr key={r.seq} className="clickable" data-testid="audit-row" onClick={() => setSel(r)}>
            <td>{r.seq}</td><td className="small mono">{fmtTs(r.ts)}</td><td className="mono">{r.event}</td>
            <td>{String(r.stage ?? r.gate ?? r.loop ?? r.question_id ?? '')}{r.unit && r.unit !== '-' ? ` · ${r.unit}` : ''}</td>
            <td>{(r.verdict || r.decision) ? <Badge v={String(r.verdict ?? r.decision)} /> : ''}</td>
            <td className="small">{String(r.actor ?? r.model ?? '')}{r.actor_type ? <span className="muted"> ({String(r.actor_type)})</span> : ''}</td>
            <td className="mono small muted">{String(r.hash).slice(0, 12)}…</td></tr>))}</tbody></table>
      </div>
      {sel && (<aside className="drawer" data-testid="audit-drawer" role="dialog" aria-label="audit record">
        <div className="row"><h2>#{sel.seq} {sel.event}</h2><div className="grow" /><button className="btn" data-testid="drawer-close" onClick={() => setSel(null)}>Close</button></div>
        <p className="small muted">prev <code>{sel.prev.slice(0, 16)}…</code> → hash <code>{sel.hash.slice(0, 16)}…</code></p>
        <pre className="block">{JSON.stringify(Object.fromEntries(Object.entries(sel).filter(([k]) => !HIDE.has(k))), null, 2)}</pre>
      </aside>)}
    </>
  )
}
