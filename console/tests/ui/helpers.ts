import { expect, type Page } from '@playwright/test'

export async function openFirstRun(page: Page) {
  await page.goto('/#/runs')
  await expect(page.getByTestId('runs-table')).toBeVisible()
  const first = page.getByTestId('run-row').first()
  const id = (await first.locator('td').first().textContent())!.trim()
  await first.click()
  await expect(page.getByTestId('current-run')).toContainText(id)
  return id
}
export async function openRun(page: Page, runId: string, tab = 'run') {
  await page.goto(`/#/${tab}/${encodeURIComponent(runId)}`)
  await expect(page.getByTestId('current-run')).toContainText(runId)
}
export const FEATURE = 'example-feature-tie-capacity'
export const RCA = 'example-rca-backfeed'
