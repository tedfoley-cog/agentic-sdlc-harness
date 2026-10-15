import { test, expect } from '@playwright/test'
import { FEATURE, openRun } from './helpers'

test('KPI cards and trend toggles', async ({ page }) => {
  await openRun(page, FEATURE, 'kpis')
  for (const k of ['autonomy', 'first_pass_rate', 'loop_resolution_rate', 'requirement_test_coverage', 'human_review_hours', 'cycle_time_minutes', 'inference_cost_per_story_point']) {
    await expect(page.getByTestId(`kpi-card-${k}`)).toBeVisible()
  }
  await expect(page.getByTestId('kpi-card-requirement_test_coverage')).toContainText('100%')
  await expect(page.getByTestId('kpi-card-loop_resolution_rate')).toContainText('100%')

  const values = page.getByTestId('trend-value')
  const before = await values.allTextContents()
  expect(before.length).toBeGreaterThanOrEqual(2)
  await expect(page.getByTestId('kpi-trend-svg')).toBeVisible()

  await page.getByTestId('trend-metric').selectOption('human_review_hours')
  const after = await values.allTextContents()
  expect(after).not.toEqual(before)
  for (const t of after) expect(t).toMatch(/ h$/)

  await page.getByTestId('trend-scope').selectOption('rca')
  await expect(page.getByTestId('trend-count')).not.toContainText(`${before.length} run`)
  const rows = page.getByTestId('trend-table').locator('tbody tr')
  for (const r of await rows.all()) await expect(r).toContainText('rca')
})
