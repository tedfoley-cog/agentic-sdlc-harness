import { test, expect } from '@playwright/test'
import { FEATURE, openRun } from './helpers'

test('timeline, gates with human actors, drill into a failing stage and a gate', async ({ page }) => {
  await openRun(page, FEATURE)
  await expect(page.getByTestId('run-status')).toHaveText('ready-to-merge')
  await expect(page.getByTestId('chain-badge-inline')).toContainText('chain intact')

  const chips = page.getByTestId('stage-chip')
  expect(await chips.count()).toBeGreaterThan(8)
  await expect(page.locator('[data-testid="stage-chip"][data-stage="qa"]').first()).toBeVisible()

  const gates = page.getByTestId('gates-table').locator('tbody tr')
  await expect(gates).toHaveCount(3)
  await expect(gates.nth(0)).toContainText('after-specify')
  await expect(gates.nth(0)).toContainText('ops-lead')
  await expect(gates.nth(2)).toContainText('before-merge')
  await expect(gates.nth(2)).toContainText('approved')

  await expect(page.getByTestId('loops-table').locator('tbody tr')).toHaveCount(5)

  await page.locator('[data-testid="stage-chip"][data-verdict="VIOLATION"]').first().click()
  const drawer = page.getByTestId('stage-drawer')
  await expect(drawer).toBeVisible()
  await expect(page.getByTestId('drawer-verdict')).toHaveText('VIOLATION')
  await expect(drawer.getByTestId('evidence-table')).toContainText('STD-ARCH-1')
  await page.getByTestId('drawer-close').click()
  await expect(drawer).toBeHidden()

  await page.locator('[data-testid="stage-chip"][data-verdict="FAIL"][data-stage="qa"]').first().click()
  await expect(page.getByTestId('drawer-verdict')).toHaveText('FAIL')
  await expect(drawer).toContainText('ultra')
  await page.getByTestId('drawer-close').click()

  await page.getByTestId('gate-chip').nth(1).click()
  await expect(drawer).toContainText('principal-engineer')
  await expect(page.getByTestId('cov-test')).toHaveText('3/3')
})
