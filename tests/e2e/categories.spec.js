const { test, expect, unique, gotoTab } = require('./fixtures');

// ISSUE-013/023: category rename/edit/delete, whitespace rejection.
test.describe('category management', () => {
  test('rename + edit description updates tab', async ({ page, api }) => {
    const type = await api.createType();
    const newName = unique('renamed');

    await page.goto('/');
    await gotoTab(page, type.name);
    await page.locator('#edit-type-btn').click();

    await expect(page.locator('#edit-type-modal')).toBeVisible();
    await expect(page.locator('#edit-type-name')).toHaveValue(type.name);
    await page.locator('#edit-type-name').fill(newName);
    await page.locator('#edit-type-description').fill('new desc');
    await page.locator('#save-edit-type-btn').click();

    await expect(page.locator('#edit-type-modal')).toBeHidden();
    await expect(page.locator('.animal-tabs .tab-btn', { hasText: newName })).toBeVisible();
  });

  test('rename keeps selected animal pedigree + active tab', async ({ page, api }) => {
    const type = await api.createType();
    await api.createAnimal({ type_id: type.id, gender: 'female', name: 'Staying', date_of_birth: '2020-01-01' });
    const newName = unique('stayed');

    await page.goto('/');
    await gotoTab(page, type.name);
    await page.locator('.animal-list-item', { hasText: 'Staying' }).locator('.animal-select-btn').click();
    await expect(page.locator('#pedigree-title')).toContainText('Staying');

    await page.locator('#edit-type-btn').click();
    await page.locator('#edit-type-name').fill(newName);
    await page.locator('#save-edit-type-btn').click();

    await expect(page.locator('#edit-type-modal')).toBeHidden();
    const renamed = page.locator('.animal-tabs .tab-btn', { hasText: newName });
    await expect(renamed).toBeVisible();
    await expect(renamed).toHaveClass(/active/);
    await expect(renamed).toHaveAttribute('aria-selected', 'true');
    // View was preserved - pedigree still shows the selected animal.
    await expect(page.locator('#pedigree-title')).toContainText('Staying');
  });

  test('delete empty category succeeds; delete with animals shows error', async ({ page, api }) => {
    const empty = await api.createType();
    const full = await api.createType();
    await api.createAnimal({ type_id: full.id, gender: 'female', name: 'Keeper', date_of_birth: '2020-01-01' });

    await page.goto('/');

    // Deleting a non-empty category shows the server error and keeps the tab.
    await gotoTab(page, full.name);
    await page.locator('#edit-type-btn').click();
    page.once('dialog', (d) => d.accept());
    await page.locator('#delete-type-btn').click();
    const errToast = page.locator('#toast-container .toast.error');
    await expect(errToast).toBeVisible();
    await expect(page.locator('.animal-tabs .tab-btn', { hasText: full.name })).toBeVisible();
    await page.keyboard.press('Escape');

    // Deleting the empty category works; tab removed.
    await gotoTab(page, empty.name);
    await page.locator('#edit-type-btn').click();
    page.once('dialog', (d) => d.accept());
    await page.locator('#delete-type-btn').click();
    await expect(page.locator('.animal-tabs .tab-btn', { hasText: empty.name })).toHaveCount(0);
  });

  test('whitespace-only category name rejected', async ({ page, api }) => {
    await api.createType();
    await page.goto('/');
    await page.locator('.tab-add').click();
    await page.locator('#new-type-name').fill('   ');
    await page.locator('#save-type-btn').click();

    await expect(page.locator('#toast-container .toast.error')).toBeVisible();
    await expect(page.locator('#add-type-modal')).toBeVisible();
  });
});
