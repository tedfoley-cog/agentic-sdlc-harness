import { useMemo, useState } from 'react'
import type { RunIndexEntry } from '../lib/types'
import { Badge, fmtTs, useSort } from '../lib/ui'

export default function RunsView({ index, onOpen }: { index: RunIndexEntry[]; onOpen: (id: string) => void }) {
  const [workflow, setWorkflow] = useState('all')
  const [status, setStatus] = useState('all')
  const [q, setQ] = useState('')
  const [sort, setSort] = useState<{ key: keyof RunIndexEntry; dir: 1 | -1 }>({ key: 'run_id', dir: 1 })
  const statuses = useMemo(() => [...new Set(index.map((e) => e.status))].sort(), [index])
  const filtered = useMemo(() => index.filter((e) =>
    (workflow === 'all' || e.workflow === workflow) && (status === 'all' || e.status === status) &&
    (q === '' || `${e.run_id} ${e.target_repo} ${e.requirement_ref ?? ''}`.toLowerCase().includes(q.toLowerCase()))), [index, workflow, status, q])
  const rows = useSort(filtered, sort.key, sort.dir)
  const th = (key: keyof RunIndexEntry, label: string) => (
    <th onClick={() => setSort((s) => ({ key, dir: s.key === key ? (s.dir === 1 ? -1 : 1) : 1 }))} data-testid={`sort-${key}`}>
      {label}{sort.key === key ? (sort.dir === 1 ? ' ▲' : ' ▼') : ''}
    </th>
  )
  return (
    <div className="panel">
      <div className="toolbar">
        <select data-testid="filter-workflow" value={workflow} onChange={(e) => setWorkflow(e.target.value)}>
          <option value="all">All workflows</option><option value="feature">feature</option><option value="rca">rca</option>
        </select>
        <select data-testid="filter-status" value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="all">All statuses</option>{statuses.map((s) => <option key={s}>{s}</option>)}
        </select>
        <input data-testid="search-runs" placeholder="Search run id, repo, requirement…" value={q} onChange={(e) => setQ(e.target.value)} />
        <span className="muted small" data-testid="runs-count">{rows.length} of {index.length} runs</span>
      </div>
      <table data-testid="runs-table">
        <thead><tr>{th('run_id', 'Run')}{th('workflow', 'Workflow')}{th('status', 'Status')}{th('target_repo', 'Target repo')}<th>Requirement</th><th>PRs</th>{th('updated', 'Exported')}</tr></thead>
        <tbody>
          {rows.map((e) => (
            <tr key={e.run_id} className="clickable" data-testid="run-row" onClick={() => onOpen(e.run_id)}>
              <td className="mono">{e.run_id}</td><td>{e.workflow}</td><td><Badge v={e.status} /></td>
              <td className="mono">{e.target_repo}</td><td className="mono small">{e.requirement_ref ?? '—'}</td>
              <td>{e.prs.map((p) => <a key={p} href={p} target="_blank" rel="noreferrer" onClick={(ev) => ev.stopPropagation()}>#{p.split('/').pop()}</a>)}</td>
              <td className="small muted">{fmtTs(e.updated)}</td>
            </tr>
          ))}
          {rows.length === 0 && <tr><td colSpan={7} className="empty" data-testid="runs-empty">No runs match the current filter.</td></tr>}
        </tbody>
      </table>
    </div>
  )
}
