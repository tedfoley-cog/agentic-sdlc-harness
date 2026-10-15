import { test, expect } from '@playwright/test'
import { RCA, openRun } from './helpers'

test('audit log: chain verified in browser, filter, search for human actor, drill in', async ({ page }) => {
  await openRun(page, RCA, 'audit')
  await expect(page.getByTestId('chain-badge')).toContainText('verified in browser')
  const rows = page.getByTestId('audit-row')
  const total = await rows.count()
  expect(total).toBeGreaterThan(15)

  await page.getByTestId('audit-event').selectOption('gate.decided')
  await expect(rows).toHaveCount(2)
  await expect(rows.first()).toContainText('protection-reviewer')
  await expect(rows.first()).toContainText('User')

  await page.getByTestId('audit-event').selectOption('all')
  await page.getByTestId('audit-search').fill('REFUTED')
  const n = await rows.count()
  expect(n).toBeGreaterThanOrEqual(1)
  expect(n).toBeLessThan(total)
  await expect(page.getByTestId('audit-count')).toContainText(`${n} of ${total}`)

  await rows.first().click()
  const drawer = page.getByTestId('audit-drawer')
  await expect(drawer).toBeVisible()
  await expect(drawer).toContainText('REFUTED')
  await expect(drawer).toContainText('evaluate')
  await page.getByTestId('drawer-close').click()
  await expect(drawer).toBeHidden()
})
