import { test, expect } from '@playwright/test'
import { FEATURE, RCA, openFirstRun } from './helpers'

test('hash routing deep links, reload persistence and run switching', async ({ page }) => {
  const first = await openFirstRun(page)
  await page.getByTestId('tab-trace').click()
  await expect(page).toHaveURL(new RegExp(`#/trace/${encodeURIComponent(first)}`))
  await page.reload()
  await expect(page.getByTestId('trace-matrix')).toBeVisible()
  await expect(page.getByTestId('current-run')).toContainText(first)

  await page.goto(`/#/audit/${RCA}`)
  await expect(page.getByTestId('current-run')).toContainText(RCA)
  await expect(page.getByTestId('audit-table')).toBeVisible()
  await page.getByTestId('tab-run').click()
  await expect(page.locator('[data-testid="stage-chip"][data-stage="evaluate"]')).toHaveCount(2)

  await page.goto(`/#/run/${FEATURE}`)
  await expect(page.locator('[data-testid="stage-chip"][data-stage="specify"]')).toHaveCount(2)
  await expect(page.locator('[data-testid="stage-chip"][data-stage="evaluate"]')).toHaveCount(0)
})
