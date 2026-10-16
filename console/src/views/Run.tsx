import { useMemo, useState } from 'react'
import type { RunBundle, StageRow } from '../lib/types'
import { Badge, KV, fmtTs, minutes, pct } from '../lib/ui'

const GATE_STAGE = /^gate:/

export default function RunView({ b }: { b: RunBundle }) {
  const [open, setOpen] = useState<StageRow | null>(null)
  const cov = useMemo(() => {
    const reqs = b.trace.requirements.filter((r) => !b.trace.waivers[r])
    const has = (k: string) => reqs.filter((r) => b.trace.rows.some((x) => x.requirement_id === r && x.kind === k)).length
    return { n: reqs.length, design: has('design'), code: has('code'), test: has('test'), pr: has('pr') }
  }, [b.trace])
  const order = b.state.plan
  const stagesFor = (step: string) => b.stages.filter((s) => step === s.stage || (step.endsWith('-loop') && step.startsWith(s.stage.split('-')[0])) ||
    (step === 'design-architect-loop' && ['design', 'architect'].includes(s.stage)) || (step === 'coding-waves' && ['coding', 'verify', 'qa'].includes(s.stage)) ||
    (step === 'fix-wave' && ['fix', 'verify', 'qa'].includes(s.stage)) || (step === 'explore-evaluate-loop' && ['explore', 'evaluate'].includes(s.stage)))
  return (
    <>
      <div className="panel">
        <div className="row">
          <h2 style={{ margin: 0, fontSize: 16 }}>{b.entry.run_id}</h2><Badge v={b.entry.workflow} /><Badge v={b.state.status} testId="run-status" />
          <span className="muted small">target <code>{b.entry.target_repo}</code> · requirement <code>{b.state.requirement_ref}</code></span>
          <div className="grow" />
          <span className="small" data-testid="chain-badge-inline">audit chain: {b.chainOk ? <b className="ok">{b.chainMessage}</b> : <b className="error">{b.chainMessage}</b>}</span>
        </div>
        {b.state.paused_on && <p className="small" data-testid="paused-on">Paused on: <code>{JSON.stringify(b.state.paused_on)}</code></p>}
      </div>
      <div className="panel">
        <h3 style={{ marginTop: 0 }}>Stage timeline</h3>
        <div className="timeline" data-testid="timeline">
          {order.filter((s) => s !== 'finish').map((step, i) => {
            if (GATE_STAGE.test(step)) {
              const g = b.gates.find((x) => `gate:${x.gate}` === step)
              return (<span key={step} className="row" style={{ gap: 8 }}>{i > 0 && <span className="arrow">→</span>}
                <button className="stage-chip gate-chip" data-testid="gate-chip" onClick={() => g && setOpen({ key: step, stage: step, unit: '-', attempt: 1, started: g.opened, completed: g.decided, verdict: (g.decision ?? 'waiting') as never, summary: g.comment, evidence: [{ kind: 'gate', ref: g.ref }], model: `${g.actor ?? '—'} (${g.actor_type ?? 'human'})` })}>
                  <div className="t">{step.replace('gate:', 'Gate · ')}</div>
                  <div className="m">{g ? <>{<Badge v={g.decision ?? 'waiting'} />} {g.actor ? <>by <b>{g.actor}</b></> : 'awaiting human'}</> : 'not reached'}</div>
                </button></span>)
            }
            const rows = stagesFor(step)
            return (<span key={step} className="row" style={{ gap: 8 }}>{i > 0 && <span className="arrow">→</span>}
              {rows.length === 0 ? <span className="stage-chip muted" style={{ borderStyle: 'dashed' }}><div className="t">{step}</div><div className="m">not reached</div></span> :
                rows.map((s) => (
                  <button key={s.key} className="stage-chip" data-testid="stage-chip" data-stage={s.stage} data-verdict={s.verdict} onClick={() => setOpen(s)}>
                    <div className="t">{s.stage}{s.unit !== '-' ? ` · ${s.unit}` : ''} <span className="muted">#{s.attempt}</span></div>
                    <div className="m"><Badge v={s.verdict ?? 'running'} /> {s.model ?? ''}</div>
                  </button>))}
            </span>)
          })}
        </div>
      </div>
      <div className="row" style={{ alignItems: 'stretch' }}>
        <div className="panel grow">
          <h3 style={{ marginTop: 0 }}>Human gates</h3>
          <table data-testid="gates-table"><thead><tr><th>Gate</th><th>Decision</th><th>Decided by</th><th>Reviewers req.</th><th>Open → decided</th><th>Record</th></tr></thead>
            <tbody>{b.gates.map((g) => (<tr key={g.gate}><td>{g.gate}</td><td><Badge v={g.decision ?? 'waiting'} /></td>
              <td>{g.actor ? <><b>{g.actor}</b> <span className="muted small">{g.actor_type}</span></> : '—'}</td><td>{g.reviewers_required ?? '—'}</td>
              <td className="small">{minutes(g.opened, g.decided) ?? '—'} min</td><td className="mono small">{g.ref.startsWith('http') ? <a href={g.ref} target="_blank" rel="noreferrer">{g.ref.split('/').slice(-2).join('/')}</a> : g.ref}</td></tr>))}
              {b.gates.length === 0 && <tr><td colSpan={6} className="muted">No gate reached yet.</td></tr>}</tbody></table>
        </div>
        <div className="panel grow">
          <h3 style={{ marginTop: 0 }}>Feedback loops</h3>
          <table data-testid="loops-table"><thead><tr><th>Loop</th><th>Unit</th><th>Iteration</th><th>Verdict</th><th>Source</th><th>Resolved</th></tr></thead>
            <tbody>{b.loops.map((l, i) => (<tr key={i}><td>{l.loop}</td><td>{l.unit}</td><td>{l.iteration}</td><td><Badge v={l.verdict} /></td><td>{l.source ?? '—'}</td><td>{l.resolved ? '✓' : '—'}</td></tr>))}
              {b.loops.length === 0 && <tr><td colSpan={6} className="muted">No loop iterations.</td></tr>}</tbody></table>
        </div>
        <div className="panel" style={{ minWidth: 260 }}>
          <h3 style={{ marginTop: 0 }}>Trace coverage</h3>
          {(['design', 'code', 'test', 'pr'] as const).map((k) => (
            <div key={k} style={{ marginBottom: 8 }}><div className="row small"><span style={{ width: 50 }}>{k}</span><span className="grow bar"><div style={{ width: pct(cov.n ? cov[k] / cov.n : 0) }} /></span><span data-testid={`cov-${k}`}>{cov[k]}/{cov.n}</span></div></div>))}
          <p className="small muted">{cov.n} requirement id(s) registered from the specification.</p>
        </div>
      </div>
      {open && (
        <aside className="drawer" data-testid="stage-drawer" role="dialog" aria-label={`${open.stage} details`}>
          <div className="row"><h2>{open.stage}{open.unit !== '-' ? ` · ${open.unit}` : ''} <span className="muted">#{open.attempt}</span></h2><div className="grow" /><button className="btn" data-testid="drawer-close" onClick={() => setOpen(null)}>Close</button></div>
          <Badge v={open.verdict ?? 'running'} testId="drawer-verdict" />
          <p>{open.summary}</p>
          <KV rows={[['model / mode', open.model ?? '—'], ['started', fmtTs(open.started)], ['completed', fmtTs(open.completed)],
            ['duration', `${minutes(open.started, open.completed) ?? '—'} min`],
            ['session', open.session_url ? <a href={open.session_url} target="_blank" rel="noreferrer">{open.session_url}</a> : '—'],
            ['brief', open.brief_ref ? <code>{open.brief_ref}</code> : '—'], ['branch / PR', <>{open.branch ?? ''} {open.pr_url && <a href={open.pr_url} target="_blank" rel="noreferrer">{open.pr_url}</a>}</>],
            ['artifacts read', (open.artifacts_read ?? []).join(', ') || '—'], ['artifacts produced', (open.artifacts_produced ?? []).join(', ') || '—']]} />
          <h3>Evidence ({open.evidence?.length ?? 0})</h3>
          <table data-testid="evidence-table"><thead><tr><th>Kind</th><th>Ref</th><th>Detail</th></tr></thead>
            <tbody>{(open.evidence ?? []).map((e, i) => <tr key={i}><td>{e.kind}</td><td className="mono small">{e.ref}</td><td className="small">{e.detail ?? ''}</td></tr>)}</tbody></table>
          {open.questions && open.questions.length > 0 && (<><h3>Questions raised</h3><ul>{open.questions.map((q) => <li key={q.id}><code>{q.id}</code> {q.question}</li>)}</ul></>)}
        </aside>
      )}
    </>
  )
}
