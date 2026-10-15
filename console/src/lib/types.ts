export type Verdict =
  | 'PASS' | 'FAIL' | 'BLOCKED' | 'CONFIRMED' | 'VIOLATION' | 'NEEDS-HUMAN'
  | 'REFUTED' | 'INSUFFICIENT_EVIDENCE' | 'RETRACTION'

export interface RunIndexEntry {
  run_id: string; workflow: 'feature' | 'rca'; status: string; target_repo: string
  requirement_ref?: string; dir: string; prs: string[]; updated: string
}
export interface LogRecord {
  seq: number; ts: string; event: string; prev: string; hash: string
  [k: string]: unknown
}
export interface StageRow {
  key: string; stage: string; unit: string; attempt: number; model?: string
  started?: string; completed?: string; verdict?: Verdict; summary?: string
  session_url?: string; evidence?: { kind: string; ref: string; detail?: string }[]
  questions?: { id: string; question: string }[]; brief_ref?: string; artifacts_read?: string[]
  artifacts_produced?: string[]; pr_url?: string; branch?: string
}
export interface GateRow {
  gate: string; ref: string; opened: string; decided?: string; decision?: string
  actor?: string; actor_type?: string; comment?: string; reviewers_required?: number
}
export interface LoopRow { loop: string; unit: string; iteration: number; verdict: string; resolved: boolean; source?: string }
export interface TraceRow { requirement_id: string; kind: string; ref: string; stage?: string; detail?: string }
export interface TraceFile { requirements: string[]; rows: TraceRow[] }
export interface Kpis {
  run_id: string; workflow: string; status: string; autonomy: number
  first_pass_approval: Record<string, boolean>; first_pass_rate: number
  loop_iterations: Record<string, number>; loop_resolution_rate: number | null
  requirement_test_coverage: number; human_review_minutes: number; human_review_hours: number
  cycle_time_minutes: number | null; acus: number; inference_cost_usd: number
  inference_cost_per_story_point: number | null; story_points: number
  gates: { gate: string; decision: string; actor: string; minutes: number }[]
  computed_at: string
}
export interface RunState {
  run_id: string; workflow: string; status: string; plan: string[]; cursor: number
  paused_on?: Record<string, unknown> | null; questions: { id: string; question: string; status: string; answer?: string; actor?: string }[]
  gates: Record<string, { status: string; ref: string; actor?: string }>; prs: string[]; units?: { id: string; title: string; depends_on: string[]; files: string[] }[]
  requirement_ref?: string; story_points?: number
}
export interface RunBundle {
  entry: RunIndexEntry; state: RunState; log: LogRecord[]; stages: StageRow[]; gates: GateRow[]
  loops: LoopRow[]; trace: TraceFile; kpis: Kpis | null; chainOk: boolean; chainMessage: string
  harnessYaml: string
}
