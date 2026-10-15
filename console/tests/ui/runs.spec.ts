import { test, expect } from '@playwright/test'
import { FEATURE, RCA } from './helpers'

test('filter, search, sort and open runs', async ({ page }) => {
  await page.goto('/#/runs')
  const rows = page.getByTestId('run-row')
  const total = await rows.count()
  expect(total).toBeGreaterThanOrEqual(2)

  await page.getByTestId('filter-workflow').selectOption('rca')
  await expect(rows.first()).toContainText('rca')
  for (const r of await rows.all()) await expect(r).toContainText('rca')
  await expect(page.getByTestId('runs-count')).toContainText(`of ${total} runs`)

  await page.getByTestId('filter-workflow').selectOption('all')
  await page.getByTestId('search-runs').fill('tie-capacity')
  await expect(rows).toHaveCount(await rows.count())
  await expect(rows.first()).toContainText(FEATURE)
  await page.getByTestId('search-runs').fill('no-such-run-xyz')
  await expect(page.getByTestId('runs-empty')).toBeVisible()
  await page.getByTestId('search-runs').fill('')

  await page.getByTestId('sort-run_id').click()
  const asc = await rows.allTextContents()
  await page.getByTestId('sort-run_id').click()
  const desc = await rows.allTextContents()
  expect(desc[0]).toBe(asc[asc.length - 1])

  await page.getByTestId('filter-status').selectOption('ready-to-merge')
  await rows.filter({ hasText: RCA }).click()
  await expect(page).toHaveURL(/#\/run\//)
  await expect(page.getByTestId('current-run')).toContainText(RCA)
})
