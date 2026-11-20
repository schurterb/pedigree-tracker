const { test, expect, gotoTab } = require('./fixtures');

// ISSUE-005: changing animal type refreshes and clears parent options.
test.describe('parent option refresh (ISSUE-005)', () => {
  test('add-form: type change reloads mothers/fathers by gender', async ({ page, api }) => {
    const typeA = await api.createType();
    const typeB = await api.createType();
    const mumA = await api.createAnimal({ type_id: typeA.id, gender: 'female', name: 'Mum A', date_of_birth: '2018-01-01' });
    await api.createAnimal({ type_id: typeA.id, gender: 'male', name: 'Dad A', date_of_birth: '2018-01-01' });
    const mumB = await api.createAnimal({ type_id: typeB.id, gender: 'female', name: 'Mum B', date_of_birth: '2018-01-01' });

    await page.goto('/');
    await gotoTab(page, typeA.name);
    await page.locator('#sidebar-add-btn').click();

    const mother = page.locator('#new-animal-mother');
    const father = page.locator('#new-animal-father');
    await expect(mother.locator('option', { hasText: 'Mum A' })).toHaveCount(1);
    await expect(mother.locator('option', { hasText: 'Dad A' })).toHaveCount(0); // males excluded
    await expect(father.locator('option', { hasText: 'Dad A' })).toHaveCount(1);
    await expect(father.locator('option', { hasText: 'Mum A' })).toHaveCount(0);

    // Select then switch type: selection must clear + list reload.
    await mother.selectOption(String(mumA.id));
    await page.locator('#new-animal-type').selectOption(String(typeB.id));
    await expect(mother).toHaveValue('');
    await expect(mother.locator('option', { hasText: 'Mum A' })).toHaveCount(0);
    await expect(mother.locator('option', { hasText: 'Mum B' })).toHaveCount(1);
  });

  test('details form: type change clears incompatible parents', async ({ page, api }) => {
    const typeA = await api.createType();
    const typeB = await api.createType();
    const mumA = await api.createAnimal({ type_id: typeA.id, gender: 'female', name: 'DM', date_of_birth: '2017-01-01' });
    const kid = await api.createAnimal({ type_id: typeA.id, gender: 'female', name: 'DKid', mother_id: mumA.id, date_of_birth: '2020-01-01' });

    await page.goto('/');
    await gotoTab(page, typeA.name);
    await page.locator('.animal-list-item', { hasText: 'DKid' }).locator('.animal-details-btn').click();
    await expect(page.locator('#animal-mother')).toHaveValue(String(mumA.id));

    await page.locator('#animal-type').selectOption(String(typeB.id));
    await expect(page.locator('#animal-mother')).toHaveValue('');
    await expect(page.locator('#animal-mother option', { hasText: 'DM' })).toHaveCount(0);
  });

  test('rapid type change ignores stale parent responses', async ({ page, api }) => {
    const typeA = await api.createType();
    const typeB = await api.createType();
    await api.createAnimal({ type_id: typeA.id, gender: 'female', name: 'Mum A', date_of_birth: '2018-01-01' });
    await api.createAnimal({ type_id: typeB.id, gender: 'female', name: 'Mum B', date_of_birth: '2018-01-01' });

    await page.goto('/');
    await gotoTab(page, typeA.name);
    await page.locator('#sidebar-add-btn').click();

    const typeSelect = page.locator('#new-animal-type');
    const mother = page.locator('#new-animal-mother');
    await expect(mother.locator('option', { hasText: 'Mum A' })).toHaveCount(1);

    // Delay type-B responses so the A->B->A switch overlaps in-flight fetches.
    await page.route(`**/animal-types/${typeB.id}/potential-parents**`, async (r) => {
      await new Promise((res) => setTimeout(res, 1500));
      await r.continue();
    });
    const bFemale = page.waitForResponse((res) =>
      res.url().includes(`/animal-types/${typeB.id}/potential-parents`) && res.url().includes('gender=female'));
    const bMale = page.waitForResponse((res) =>
      res.url().includes(`/animal-types/${typeB.id}/potential-parents`) && res.url().includes('gender=male'));

    await typeSelect.selectOption(String(typeB.id));
    await typeSelect.selectOption(String(typeA.id));

    await Promise.all([bFemale, bMale]);
    // Let the stale response's JS fill run so a regression would append Mum B.
    await page.waitForTimeout(300);

    await expect(typeSelect).toHaveValue(String(typeA.id));
    await expect(mother.locator('option', { hasText: 'Mum B' })).toHaveCount(0);
    await expect(mother.locator('option', { hasText: 'Mum A' })).toHaveCount(1);
  });
});
