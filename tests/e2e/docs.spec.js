const { test, expect } = require('./fixtures');

// ISSUE-016/017: swagger.json valid; docs works with and without slash.
test.describe('swagger docs', () => {
  test('swagger.json returns 200 with paths', async ({ baseURL }) => {
    const res = await fetch(`${baseURL}/api/v1/swagger.json`);
    expect(res.ok).toBeTruthy();
    const spec = await res.json();
    expect(spec.paths).toBeTruthy();
    expect(Object.keys(spec.paths)).toContain('/animals/{id}');
  });

  for (const path of ['/api/v1/docs', '/api/v1/docs/']) {
    test(`${path} renders Swagger UI operations`, async ({ page }) => {
      const response = await page.goto(path);
      expect(response.ok()).toBeTruthy();
      // Swagger UI loads spec sections, not "Failed to load spec".
      await expect(page.locator('.opblock-tag').first()).toBeVisible({ timeout: 15_000 });
      await expect(page.locator('.opblock-tag', { hasText: 'animals' })).toBeVisible();
      await expect(page.locator('body')).not.toContainText('Failed to load');
    });
  }
});
