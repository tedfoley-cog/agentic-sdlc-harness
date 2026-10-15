import { test, expect } from '@playwright/test'
import { FEATURE, openRun } from './helpers'

test('trace matrix coverage, filter by kind, search and sort', async ({ page }) => {
  await openRun(page, FEATURE, 'trace')
  await expect(page.getByTestId('trace-coverage')).toContainText('3/3 fully traced (100%)')
  const reqs = page.getByTestId('trace-req')
  await expect(reqs).toHaveCount(3)
  for (const r of await reqs.all()) await expect(r).toHaveAttribute('data-complete', 'true')

  const rows = page.getByTestId('trace-row')
  const all = await rows.count()
  await page.getByTestId('trace-kind').selectOption('test')
  await expect(rows).toHaveCount(3)
  for (const r of await rows.all()) await expect(r.locator('td').nth(1)).toHaveText('test')

  await page.getByTestId('trace-kind').selectOption('all')
  await expect(rows).toHaveCount(all)
  await page.getByTestId('trace-search').fill('REQ-FLISR-103')
  expect(await rows.count()).toBeLessThan(all)
  for (const r of await rows.all()) await expect(r).toContainText('REQ-FLISR-103')
  await page.getByTestId('trace-search').fill('')

  await page.getByTestId('sort-ref').click()
  const asc = await rows.locator('td:nth-child(3)').allTextContents()
  await page.getByTestId('sort-ref').click()
  const desc = await rows.locator('td:nth-child(3)').allTextContents()
  expect(desc).toEqual([...asc].reverse())
})
