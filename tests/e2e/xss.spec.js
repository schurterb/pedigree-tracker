const { test, expect, gotoTab } = require('./fixtures');

// Stored-XSS fix: malicious names render as literal text.
test.describe('stored XSS (tree nodes)', () => {
  test('script payload in name renders literally, no code runs', async ({ page, api }) => {
    const type = await api.createType();
    const payload = '<img src=x onerror="window.__xss=1">';
    await api.createAnimal({ type_id: type.id, gender: 'female', name: payload, date_of_birth: '2020-01-01' });

    await page.goto('/');
    await gotoTab(page, type.name);
    await page.locator('.animal-list-item').first().locator('.animal-select-btn').click();
    await expect(page.locator('#pedigree-tree')).toBeVisible();

    // The payload appears as literal text in the node.
    await expect(page.locator('#pedigree-tree')).toContainText('<img');
    // No img element injected inside nodes, no handler executed.
    await expect(page.locator('#pedigree-tree img[src="x"]')).toHaveCount(0);
    expect(await page.evaluate(() => window.__xss)).toBeUndefined();
  });
});
