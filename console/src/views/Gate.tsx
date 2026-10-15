import { useMemo, useState } from 'react'
import type { RunBundle } from '../lib/types'

// Humans decide here. The form never writes to the run: it produces the decision record
// (and the equivalent GitHub label command) that a person applies in the system of record.
export default function GateView({ b }: { b: RunBundle }) {
  const waiting = useMemo(() => b.gates.filter((g) => !g.decision), [b.gates])
  const [gate, setGate] = useState(waiting[0]?.gate ?? b.gates[0]?.gate ?? 'after-specify')
  const [decision, setDecision] = useState<'approved' | 'rejected' | ''>('')
  const [actor, setActor] = useState('')
  const [comment, setComment] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [out, setOut] = useState<string | null>(null)

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    const errs: Record<string, string> = {}
    if (!decision) errs.decision = 'Choose approve or reject — the harness never infers a decision.'
    if (!/^[a-z0-9](?:[a-z0-9-]{0,37}[a-z0-9])?$/i.test(actor)) errs.actor = 'GitHub login of the human decision-maker is required (no bots, no service accounts).'
    if (decision === 'rejected' && comment.trim().length < 10) errs.comment = 'A rejection needs a reason of at least 10 characters so the stage can act on it.'
    setErrors(errs)
    if (Object.keys(errs).length) { setOut(null); return }
    const record = { gate, decision, actor, actor_type: 'User', comment: comment.trim(), decided_at: new Date().toISOString(), run_id: b.entry.run_id }
    const label = decision === 'approved' ? 'gate:approved' : 'gate:rejected'
    const ref = b.gates.find((g) => g.gate === gate)?.ref ?? ''
    const issue = ref.match(/issues\/(\d+)/)?.[1]
    setOut([`# decision record → runs/${b.entry.dir}/gates/${gate}.decision.json`, JSON.stringify(record, null, 2), '',
      issue ? `# or, in the system of record:\ngh issue edit ${issue} --repo ${b.entry.target_repo} --add-label ${label}\ngh issue comment ${issue} --repo ${b.entry.target_repo} --body "${record.comment || decision}"` : '# gate issue not yet opened for this gate',
      `harness resume ${b.entry.run_id}`].join('\n'))
  }
  return (
    <div className="panel">
      <h3 style={{ marginTop: 0 }}>Record a human gate decision</h3>
      <p className="small muted">Agents stop at <b>after-specify</b>, <b>after-architect</b>/<b>after-review</b> and <b>before-merge</b>. Only a human account can approve or reject; the decision and the actor are written to the audit log.</p>
      <form className="gate" onSubmit={submit} noValidate data-testid="gate-form">
        <label htmlFor="g">Gate</label>
        <select id="g" data-testid="gate-name" value={gate} onChange={(e) => setGate(e.target.value)}>
          {(b.gates.length ? b.gates : [{ gate: 'after-specify', decision: undefined }]).map((g) => <option key={g.gate} value={g.gate}>{g.gate}{g.decision ? ` (already ${g.decision})` : ' (waiting)'}</option>)}
        </select>
        <label>Decision</label>
        <div className="row">
          <label className="row" style={{ fontWeight: 400 }}><input type="radio" name="d" data-testid="gate-approve" checked={decision === 'approved'} onChange={() => setDecision('approved')} /> Approve</label>
          <label className="row" style={{ fontWeight: 400 }}><input type="radio" name="d" data-testid="gate-reject" checked={decision === 'rejected'} onChange={() => setDecision('rejected')} /> Reject</label>
        </div>
        {errors.decision && <div className="error" data-testid="error-decision">{errors.decision}</div>}
        <label htmlFor="a">Decision-maker (GitHub login)</label>
        <input id="a" data-testid="gate-actor" value={actor} onChange={(e) => setActor(e.target.value)} placeholder="e.g. jane-doe" />
        {errors.actor && <div className="error" data-testid="error-actor">{errors.actor}</div>}
        <label htmlFor="c">Comment {decision === 'rejected' ? '(required for rejections)' : '(optional)'}</label>
        <textarea id="c" data-testid="gate-comment" rows={3} value={comment} onChange={(e) => setComment(e.target.value)} />
        {errors.comment && <div className="error" data-testid="error-comment">{errors.comment}</div>}
        <div style={{ marginTop: 12 }}><button className="btn primary" type="submit" data-testid="gate-submit">Produce decision record</button></div>
      </form>
      {out && <pre className="block" data-testid="gate-output" style={{ marginTop: 14 }}>{out}</pre>}
    </div>
  )
}
