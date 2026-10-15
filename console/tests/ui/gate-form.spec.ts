import { test, expect } from '@playwright/test'
import { FEATURE, openRun } from './helpers'

test('gate decision form validates and produces a human decision record', async ({ page }) => {
  await openRun(page, FEATURE, 'gate')
  await page.getByTestId('gate-submit').click()
  await expect(page.getByTestId('error-decision')).toBeVisible()
  await expect(page.getByTestId('error-actor')).toBeVisible()
  await expect(page.getByTestId('gate-output')).toBeHidden()

  await page.getByTestId('gate-reject').check()
  await page.getByTestId('gate-actor').fill('devin[bot]')
  await page.getByTestId('gate-submit').click()
  await expect(page.getByTestId('error-decision')).toBeHidden()
  await expect(page.getByTestId('error-actor')).toContainText('human')
  await expect(page.getByTestId('error-comment')).toContainText('at least 10 characters')

  await page.getByTestId('gate-actor').fill('jane-doe')
  await page.getByTestId('gate-comment').fill('Tie capacity source still ambiguous; respecify.')
  await page.getByTestId('gate-name').selectOption('after-specify')
  await page.getByTestId('gate-submit').click()
  const out = page.getByTestId('gate-output')
  await expect(out).toBeVisible()
  await expect(out).toContainText('"decision": "rejected"')
  await expect(out).toContainText('"actor": "jane-doe"')
  await expect(out).toContainText('"actor_type": "User"')
  await expect(out).toContainText(`harness resume ${FEATURE}`)
})
