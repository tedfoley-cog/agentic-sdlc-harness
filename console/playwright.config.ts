import { defineConfig } from '@playwright/test'

// The gauntlet runs against the built console (vite preview on 4173) so CI exercises the same
// static bundle a reviewer would open. `npm --prefix console run build` syncs ../runs first.
export default defineConfig({
  testDir: './tests/ui',
  timeout: 30_000,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['list'], ['html', { open: 'never', outputFolder: '../playwright-report' }]] : 'list',
  use: { baseURL: 'http://127.0.0.1:4173', headless: true, viewport: { width: 1400, height: 900 }, screenshot: 'only-on-failure' },
  webServer: {
    command: 'npm run build && npm run preview -- --host 127.0.0.1',
    url: 'http://127.0.0.1:4173',
    reuseExistingServer: !process.env.CI,
    timeout: 180_000,
  },
  projects: [{ name: 'chromium', use: { browserName: 'chromium' } }],
})
