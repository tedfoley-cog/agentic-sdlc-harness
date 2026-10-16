import type { GateRow, LogRecord, LoopRow, RunBundle, RunIndexEntry, StageRow, TraceFile, TraceRow, Kpis, RunState } from './types'

const base = () => `${import.meta.env.BASE_URL.replace(/\/$/, '')}/runs`

async function text(path: string): Promise<string | null> {
  const r = await fetch(`${base()}/${path}`, { cache: 'no-store' })
  return r.ok ? r.text() : null
}
async function json<T>(path: string): Promise<T | null> {
  const t = await text(path)
  if (t == null) return null
  try { return JSON.parse(t) as T } catch { return null }
}

export async function loadIndex(): Promise<RunIndexEntry[]> {
  return (await json<RunIndexEntry[]>('index.json')) ?? []
}
export async function loadKpiHistory(): Promise<Kpis[]> {
  const t = await text('kpi_history.jsonl')
  return (t ?? '').split('\n').filter(Boolean).map((l) => JSON.parse(l) as Kpis)
}

export async function sha256Hex(s: string): Promise<string> {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s))
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, '0')).join('')
}

// Mirrors agentic_sdlc.runlog.RunLog.verify_chain: hash = sha256(canonical json(record without hash)),
// canonical = sorted keys, compact separators, ASCII-escaped strings (Python json.dumps defaults).
function canonical(v: unknown): string {
  if (typeof v === 'string') return JSON.stringify(v).replace(/[\u007f-\uffff]/g, (c) => `\\u${c.charCodeAt(0).toString(16).padStart(4, '0')}`)
  if (v === null || typeof v !== 'object') return JSON.stringify(v)
  if (Array.isArray(v)) return `[${v.map(canonical).join(',')}]`
  const o = v as Record<string, unknown>
  return `{${Object.keys(o).sort().map((k) => `${JSON.stringify(k)}:${canonical(o[k])}`).join(',')}}`
}
export async function verifyChain(log: LogRecord[]): Promise<{ ok: boolean; message: string }> {
  let prev = '0'.repeat(64)
  for (const rec of log) {
    const { hash, ...rest } = rec
    if (rest.prev !== prev) return { ok: false, message: `broken link at seq ${rec.seq}` }
    const expected = await sha256Hex(canonical(rest))
    if (expected !== hash) return { ok: false, message: `hash mismatch at seq ${rec.seq}` }
    prev = hash
  }
  return { ok: true, message: `chain intact (${log.length} records)` }
}

export function deriveStages(log: LogRecord[]): StageRow[] {
  const map = new Map<string, StageRow>()
  for (const r of log) {
    if (r.event !== 'stage.started' && r.event !== 'stage.completed') continue
    const key = `${r.stage}:${r.unit}:${r.attempt}`
    const row = map.get(key) ?? { key, stage: String(r.stage), unit: String(r.unit), attempt: Number(r.attempt) }
    if (r.event === 'stage.started') {
      Object.assign(row, { started: r.ts, model: r.model, brief_ref: r.brief_ref, artifacts_read: r.artifacts_read })
    } else {
      Object.assign(row, {
        completed: r.ts, verdict: r.verdict, summary: r.summary, session_url: r.session_url, evidence: r.evidence,
        questions: r.questions, artifacts_produced: r.artifacts_produced, pr_url: r.pr_url, branch: r.branch,
        model: r.model ?? row.model,
      })
    }
    map.set(key, row)
  }
  return [...map.values()]
}
export function deriveGates(log: LogRecord[]): GateRow[] {
  const gates = new Map<string, GateRow>()
  for (const r of log) {
    if (r.event === 'gate.opened') gates.set(String(r.gate), { gate: String(r.gate), ref: String(r.ref), opened: r.ts, reviewers_required: r.reviewers_required as number | undefined })
    if (r.event === 'gate.decided') {
      const g = gates.get(String(r.gate)) ?? { gate: String(r.gate), ref: '', opened: r.ts }
      Object.assign(g, { decided: r.ts, decision: r.decision, actor: r.actor, actor_type: r.actor_type, comment: r.comment })
      gates.set(String(r.gate), g)
    }
  }
  return [...gates.values()]
}
export function deriveLoops(log: LogRecord[]): LoopRow[] {
  // Older logs (before loop.iteration became idempotent) may carry the same record twice after a
  // pause/resume replay; collapse exact repeats only — a round's FAIL (verify) and later PASS (qa) both stay.
  const byKey = new Map<string, LoopRow>()
  for (const r of log.filter((r) => r.event === 'loop.iteration')) {
    const unit = r.unit == null ? '-' : String(r.unit)
    byKey.set(`${r.loop}:${unit}:${r.iteration}:${r.source ?? '-'}:${r.verdict}:${r.resolved}`, {
      loop: String(r.loop), unit, iteration: Number(r.iteration), verdict: String(r.verdict),
      resolved: Boolean(r.resolved), source: (r.source as string | undefined) ?? (Array.isArray(r.findings) && r.findings.length ? `${r.findings.length} finding(s)` : undefined),
    })
  }
  return [...byKey.values()]
}

// trace.json stores requirements as {id: {source...}}; the console only needs the ordered id list.
function normalizeTrace(t: unknown): TraceFile {
  const o = (t ?? {}) as { requirements?: unknown; rows?: TraceRow[]; waivers?: TraceFile['waivers'] }
  const reqs = Array.isArray(o.requirements) ? (o.requirements as string[]) : Object.keys((o.requirements as object) ?? {})
  return { requirements: reqs, rows: Array.isArray(o.rows) ? o.rows : [], waivers: o.waivers ?? {} }
}

export async function loadRun(entry: RunIndexEntry): Promise<RunBundle> {
  const [state, logText, trace, kpis, harnessYaml] = await Promise.all([
    json<RunState>(`${entry.dir}/state.json`), text(`${entry.dir}/runlog.jsonl`),
    json<TraceFile>(`${entry.dir}/trace.json`), json<Kpis>(`${entry.dir}/kpis.json`), text(`${entry.dir}/harness.yaml`),
  ])
  const log = (logText ?? '').split('\n').filter(Boolean).map((l) => JSON.parse(l) as LogRecord)
  const chain = await verifyChain(log)
  return {
    entry, state: state as RunState, log, stages: deriveStages(log), gates: deriveGates(log), loops: deriveLoops(log),
    trace: normalizeTrace(trace), kpis, chainOk: chain.ok, chainMessage: chain.message,
    harnessYaml: harnessYaml ?? '',
  }
}
