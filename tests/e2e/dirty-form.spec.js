const { test, expect, gotoTab } = require('./fixtures');

// ISSUE-019: unsaved changes require confirmation before navigating away.
test.describe('dirty form guard (ISSUE-019)', () => {
  test('switching tab with unsaved details prompts; dismiss keeps edits', async ({ page, api }) => {
    const type = await api.createType();
    const other = await api.createType();
    const a = await api.createAnimal({ type_id: type.id, gender: 'female', name: 'Dirty A', date_of_birth: '2020-01-01' });

    await page.goto('/');
    await gotoTab(page, type.name);
    await page.locator('.animal-list-item', { hasText: 'Dirty A' }).locator('.animal-details-btn').click();
    await page.locator('#animal-notes').fill('unsaved note');

    // Dismiss the confirm -> stays on the form, data intact.
    page.once('dialog', (d) => d.dismiss());
    await gotoTab(page, other.name);
    await expect(page.locator('#details-view')).toBeVisible();
    await expect(page.locator('#animal-notes')).toHaveValue('unsaved note');

    // Accept -> navigation proceeds.
    page.once('dialog', (d) => d.accept());
    await gotoTab(page, other.name);
    await expect(page.locator('#details-view')).not.toBeVisible();
  });

  test('add-category (+) with unsaved draft prompts; dismiss keeps draft', async ({ page, api }) => {
    await api.createType();
    await page.goto('/');
    await page.locator('#sidebar-add-btn').click();
    await page.locator('#new-animal-id').fill('DRAFT-1');

    // Dismiss -> modal never opens, draft intact.
    page.once('dialog', (d) => d.dismiss());
    await page.locator('.tab-add').click();
    await expect(page.locator('#add-type-modal')).toBeHidden();
    await expect(page.locator('#new-animal-id')).toHaveValue('DRAFT-1');

    // Accept -> modal opens.
    page.once('dialog', (d) => d.accept());
    await page.locator('.tab-add').click();
    await expect(page.locator('#add-type-modal')).toBeVisible();
  });

  test('edit-category (pencil) with unsaved details prompts', async ({ page, api }) => {
    const type = await api.createType();
    await api.createAnimal({ type_id: type.id, gender: 'female', name: 'Guard Me', date_of_birth: '2020-01-01' });

    await page.goto('/');
    await gotoTab(page, type.name);
    await page.locator('.animal-list-item', { hasText: 'Guard Me' }).locator('.animal-details-btn').click();
    await page.locator('#animal-notes').fill('unsaved note');

    page.once('dialog', (d) => d.dismiss());
    await page.locator('#edit-type-btn').click();
    await expect(page.locator('#edit-type-modal')).toBeHidden();
    await expect(page.locator('#animal-notes')).toHaveValue('unsaved note');

    page.once('dialog', (d) => d.accept());
    await page.locator('#edit-type-btn').click();
    await expect(page.locator('#edit-type-modal')).toBeVisible();
  });

  test('clean form: + opens modal with no confirm', async ({ page, api }) => {
    await api.createType();
    await page.goto('/');

    let dialogs = 0;
    page.on('dialog', (d) => { dialogs++; d.dismiss(); });
    await page.locator('.tab-add').click();
    await expect(page.locator('#add-type-modal')).toBeVisible();
    expect(dialogs).toBe(0);
  });
});
