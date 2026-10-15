import { cpSync, existsSync, mkdirSync, rmSync } from 'node:fs'
const src = new URL('../runs/', import.meta.url)
const dst = new URL('./public/runs/', import.meta.url)
if (existsSync(dst)) rmSync(dst, { recursive: true })
mkdirSync(dst, { recursive: true })
cpSync(src, dst, { recursive: true, filter: (p) => !p.includes('fake_script') })
console.log('synced runs ->', dst.pathname)
