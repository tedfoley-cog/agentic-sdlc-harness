import { useMemo, useState } from 'react'
import type { RunBundle, TraceRow } from '../lib/types'
import { Badge, pct, useSort } from '../lib/ui'

export default function TraceView({ b }: { b: RunBundle }) {
  const [kind, setKind] = useState('all')
  const [q, setQ] = useState('')
  const [sort, setSort] = useState<{ key: keyof TraceRow; dir: 1 | -1 }>({ key: 'requirement_id', dir: 1 })
  const reqs = b.trace.requirements
  const matrix = useMemo(() => reqs.map((r) => {
    const rows = b.trace.rows.filter((x) => x.requirement_id === r)
    const k = (kk: string) => rows.filter((x) => x.kind === kk).map((x) => x.ref)
    return { requirement_id: r, design: k('design'), code: k('code'), test: k('test'), pr: k('pr'), doc: k('doc'), complete: ['design', 'code', 'test', 'pr'].every((kk) => k(kk).length > 0) }
  }), [reqs, b.trace.rows])
  const filteredRows = useMemo(() => b.trace.rows.filter((r) => (kind === 'all' || r.kind === kind) &&
    (q === '' || `${r.requirement_id} ${r.ref} ${r.stage ?? ''}`.toLowerCase().includes(q.toLowerCase()))), [b.trace.rows, kind, q])
  const rows = useSort(filteredRows, sort.key, sort.dir)
  const th = (key: keyof TraceRow, label: string) => (
    <th data-testid={`sort-${key}`} onClick={() => setSort((s) => ({ key, dir: s.key === key ? (s.dir === 1 ? -1 : 1) : 1 }))}>{label}{sort.key === key ? (sort.dir === 1 ? ' ▲' : ' ▼') : ''}</th>)
  const covered = matrix.filter((m) => m.complete).length
  return (
    <>
      <div className="panel">
        <div className="row"><h3 style={{ margin: 0 }}>Requirement → design → code → test → PR</h3><div className="grow" />
          <span data-testid="trace-coverage">{covered}/{reqs.length} fully traced ({pct(reqs.length ? covered / reqs.length : 0)})</span></div>
        <div className="bar" style={{ margin: '8px 0 12px' }}><div style={{ width: pct(reqs.length ? covered / reqs.length : 0) }} /></div>
        <table data-testid="trace-matrix"><thead><tr><th>Requirement</th><th>Design</th><th>Code</th><th>Test</th><th>PR</th><th>Doc</th><th>Status</th></tr></thead>
          <tbody>{matrix.map((m) => (<tr key={m.requirement_id} data-testid="trace-req" data-complete={m.complete}>
            <td className="mono">{m.requirement_id}</td>
            {(['design', 'code', 'test', 'pr', 'doc'] as const).map((k) => <td key={k} className="small mono">{m[k].length ? m[k].join(', ') : <span className="error">missing</span>}</td>)}
            <td><Badge v={m.complete ? 'PASS' : 'FAIL'} /></td></tr>))}
            {matrix.length === 0 && <tr><td colSpan={7} className="muted">No requirement ids registered yet (Specify has not passed).</td></tr>}</tbody></table>
      </div>
      <div className="panel">
        <div className="toolbar"><h3 style={{ margin: 0 }}>Trace rows ({rows.length})</h3>
          <select data-testid="trace-kind" value={kind} onChange={(e) => setKind(e.target.value)}><option value="all">All kinds</option>{['design', 'code', 'test', 'pr', 'doc'].map((k) => <option key={k}>{k}</option>)}</select>
          <input data-testid="trace-search" placeholder="Search requirement / ref" value={q} onChange={(e) => setQ(e.target.value)} /></div>
        <table data-testid="trace-table"><thead><tr>{th('requirement_id', 'Requirement')}{th('kind', 'Kind')}{th('ref', 'Ref')}{th('stage', 'Added by stage')}</tr></thead>
          <tbody>{rows.map((r, i) => <tr key={i} data-testid="trace-row"><td className="mono">{r.requirement_id}</td><td>{r.kind}</td><td className="mono small">{r.ref}</td><td>{r.stage ?? '—'}</td></tr>)}</tbody></table>
      </div>
    </>
  )
}
