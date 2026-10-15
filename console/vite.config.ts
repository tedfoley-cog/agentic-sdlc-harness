import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The console is a static viewer over the harness' run directory. `npm run sync-runs`
// copies ../runs into public/runs so dev, preview and the built site all read the same files.
export default defineConfig({
  plugins: [react()],
  base: './',
  server: { port: 5173, strictPort: true },
  preview: { port: 4173, strictPort: true },
})
