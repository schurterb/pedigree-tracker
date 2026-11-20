const { test, expect, gotoTab } = require('./fixtures');

// ISSUE-004: Jan 1 DOB must render correct year in every timezone project.
test.describe('date rendering (ISSUE-004)', () => {
  test('Jan 1 DOB shows correct year in tree, details, offspring', async ({ page, api }) => {
    const type = await api.createType();
    const dam = await api.createAnimal({
      type_id: type.id, gender: 'female', name: 'New Year Dam', date_of_birth: '2020-01-01',
    });
    const kid = await api.createAnimal({
      type_id: type.id, gender: 'male', name: 'New Year Kid', date_of_birth: '2022-06-15', mother_id: dam.id,
    });

    await page.goto('/');
    await gotoTab(page, type.name);

    // Pedigree node shows "Born: 2020" (not 2019 from UTC-shift).
    await page.locator('.animal-list-item', { hasText: 'New Year Kid' }).locator('.animal-select-btn').click();
    await expect(page.locator('#pedigree-tree')).toContainText('Born: 2020');
    await expect(page.locator('#pedigree-tree')).toContainText('New Year Dam');

    // Details input shows the exact ISO date.
    await page.locator('.animal-list-item', { hasText: 'New Year Dam' }).locator('.animal-details-btn').click();
    await expect(page.locator('#animal-dob')).toHaveValue('2020-01-01');

    // Offspring list renders dates as MM/DD/YYYY without shift.
    await expect(page.locator('#offspring-list')).toContainText('New Year Kid');
    await expect(page.locator('#offspring-list')).toContainText('06/15/2022');
  });
});
