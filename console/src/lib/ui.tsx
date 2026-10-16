import { Fragment, type ReactNode } from 'react'

export const Badge = ({ v, testId }: { v?: string; testId?: string }) => (
  <span className={`badge v-${v ?? 'neutral'}`} data-testid={testId}>{v ?? '—'}</span>
)
export const pct = (x: number | null | undefined) => (x == null ? '—' : `${Math.round(x * 100)}%`)
export const fmtTs = (s?: string) => (s ? s.replace('T', ' ').replace(/\.\d+Z?$/, 'Z') : '—')
export const minutes = (a?: string, b?: string) => (a && b ? Math.round((+new Date(b) - +new Date(a)) / 60000) : null)
export const KV = ({ rows }: { rows: [string, ReactNode][] }) => (
  <dl className="kv">{rows.map(([k, v]) => (<Fragment key={k}><dt>{k}</dt><dd>{v}</dd></Fragment>))}</dl>
)
export function useSort<T>(rows: T[], key: keyof T | null, dir: 1 | -1): T[] {
  if (!key) return rows
  return [...rows].sort((a, b) => {
    const x = a[key], y = b[key]
    if (x === y) return 0
    if (x == null) return 1
    if (y == null) return -1
    return (x < y ? -1 : 1) * dir
  })
}
