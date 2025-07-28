import { test, expect } from '@playwright/test'

test.describe('Z2 Platform Basic Navigation', () => {
  test('should load homepage successfully', async ({ page }) => {
    await page.goto('/')
    
    // Check if the page loads and has the expected title
    await expect(page).toHaveTitle(/Z2/)
    
    // Check for main navigation elements
    await expect(page.locator('body')).toBeVisible()
  })

  test('should have basic responsive design', async ({ page }) => {
    await page.goto('/')
    
    // Test different viewport sizes
    await page.setViewportSize({ width: 1920, height: 1080 })
    await expect(page.locator('body')).toBeVisible()
    
    await page.setViewportSize({ width: 768, height: 1024 })
    await expect(page.locator('body')).toBeVisible()
    
    await page.setViewportSize({ width: 375, height: 667 })
    await expect(page.locator('body')).toBeVisible()
  })

  test('should have accessible navigation', async ({ page }) => {
    await page.goto('/')
    
    // Test keyboard navigation
    await page.keyboard.press('Tab')
    
    // Verify that focus is visible
    const focusedElement = await page.locator(':focus')
    await expect(focusedElement).toBeVisible()
  })
})