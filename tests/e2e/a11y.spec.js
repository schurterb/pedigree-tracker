const { test, expect, gotoTab } = require('./fixtures');

// ISSUE-020/021: modal dialog semantics + keyboard row selection.
test.describe('accessibility', () => {
  test('modal: dialog role, focus trap, Escape closes, focus restored', async ({ page, api }) => {
    await api.createType();
    await page.goto('/');

    const addTab = page.locator('.tab-add');
    await addTab.focus();
    await addTab.press('Enter');

    const dialog = page.locator('#add-type-modal .modal-content');
    await expect(dialog).toBeVisible();
    await expect(dialog).toHaveAttribute('role', 'dialog');
    await expect(dialog).toHaveAttribute('aria-modal', 'true');

    // Focus moved inside the dialog.
    const inside = await page.evaluate(() =>
      document.getElementById('add-type-modal').contains(document.activeElement));
    expect(inside).toBeTruthy();

    // Tab cycles within the dialog (never leaves it).
    for (let i = 0; i < 8; i++) {
      await page.keyboard.press('Tab');
      const stillInside = await page.evaluate(() =>
        document.getElementById('add-type-modal').contains(document.activeElement));
      expect(stillInside).toBeTruthy();
    }
    // Shift+Tab likewise stays inside.
    await page.keyboard.press('Shift+Tab');
    const insideAfter = await page.evaluate(() =>
      document.getElementById('add-type-modal').contains(document.activeElement));
    expect(insideAfter).toBeTruthy();

    // Escape closes and focus returns to the trigger.
    await page.keyboard.press('Escape');
    await expect(page.locator('#add-type-modal')).toBeHidden();
    await expect(addTab).toBeFocused();
  });

  test('animal row reachable by keyboard; Enter loads pedigree', async ({ page, api }) => {
    const type = await api.createType();
    await api.createAnimal({ type_id: type.id, gender: 'female', name: 'Keys', date_of_birth: '2020-01-01' });

    await page.goto('/');
    await gotoTab(page, type.name);

    const row = page.locator('.animal-list-item', { hasText: 'Keys' }).locator('.animal-select-btn');
    await row.focus();
    await expect(row).toBeFocused();
    await row.press('Enter');
    await expect(page.locator('#pedigree-title')).toContainText('Keys');
    await expect(row).toHaveAttribute('aria-current', 'true');
  });
});
