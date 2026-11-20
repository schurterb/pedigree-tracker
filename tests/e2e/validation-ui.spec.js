const { test, expect, gotoTab } = require('./fixtures');

// ISSUE-012/015: future DOB rejected, error shown, no SQL/exception leakage.
test.describe('validation UI', () => {
  test('future DOB shows field error toast without SQL', async ({ page, api }) => {
    const type = await api.createType();
    await page.goto('/');
    await gotoTab(page, type.name);
    await page.locator('#sidebar-add-btn').click();
    await page.locator('#new-animal-id').fill('FUT-1');
    await page.locator('#new-animal-dob').fill('2999-01-01');
    await page.locator('#save-new-btn').click();

    const toast = page.locator('#toast-container .toast.error');
    await expect(toast).toBeVisible();
    const text = await toast.textContent();
    expect(text.toLowerCase()).toContain('birth');
    for (const bad of ['SELECT', 'INSERT', 'sqlite', 'IntegrityError', 'Traceback']) {
      expect(text).not.toContain(bad);
    }
    // Form stays open so user can fix the field.
    await expect(page.locator('#add-animal-view')).toBeVisible();
  });
});
