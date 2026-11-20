const { test, expect, unique, gotoTab, selectAnimalRow } = require('./fixtures');

// ISSUE-001/002/003: creation without DOB, item routing, create-flow state.
test.describe('core flow', () => {
  test('create animal without DOB -> pedigree view, form cleared', async ({ page, api }) => {
    const type = await api.createType();
    const identifier = unique('COW');

    await page.goto('/');
    await gotoTab(page, type.name);
    await page.locator('#sidebar-add-btn').click();
    await page.locator('#new-animal-id').fill(identifier);
    await page.locator('#new-animal-name').fill('Bessie');
    // Leave DOB blank (ISSUE-001).
    await page.locator('#save-new-btn').click();

    await expect(page.locator('#toast-container .toast.success')).toContainText('added successfully');
    // ISSUE-003: must leave create mode and show pedigree, not a populated form.
    await expect(page.locator('#add-animal-view')).not.toBeVisible();
    await expect(page.locator('#pedigree-view')).toBeVisible();
    await expect(page.locator('#pedigree-title')).toContainText('Bessie');
    // Form fields cleared for next use.
    await expect(page.locator('#new-animal-id')).toHaveValue('');
    // Animal appears in the sidebar.
    await expect(page.locator('.animal-list-item', { hasText: 'Bessie' })).toBeVisible();
  });

  test('double-click save sends a single POST', async ({ page, api }) => {
    const type = await api.createType();
    await page.goto('/');
    await gotoTab(page, type.name);
    await page.locator('#sidebar-add-btn').click();
    await page.locator('#new-animal-id').fill(unique('DBL'));

    let posts = 0;
    page.on('request', (r) => {
      if (r.method() === 'POST' && r.url().includes('/api/v1/animals')) posts++;
    });
    await page.locator('#save-new-btn').dispatchEvent('click');
    await page.locator('#save-new-btn').dispatchEvent('click');

    await expect(page.locator('#toast-container .toast.success')).toBeVisible();
    expect(posts).toBe(1);
  });

  test('create succeeds but pedigree load fails -> specific toast, form closed', async ({ page, api }) => {
    const type = await api.createType();
    await page.goto('/');
    await gotoTab(page, type.name);
    await page.locator('#sidebar-add-btn').click();

    // Simulate the follow-up read failing after creation. 404 keeps the
    // fixtures' real-5xx guard quiet while exercising the failure path.
    await page.route(/\/api\/v1\/animals\/\d+\/pedigree/, (r) =>
      r.fulfill({ status: 404, contentType: 'application/json', body: JSON.stringify({ message: 'Simulated failure' }) })
    );

    let posts = 0;
    page.on('request', (r) => {
      if (r.method() === 'POST' && r.url().includes('/api/v1/animals')) posts++;
    });

    await page.locator('#new-animal-id').fill(unique('FAIL'));
    await page.locator('#new-animal-name').fill('Partial Win');
    await page.locator('#save-new-btn').click();

    // One specific error toast; no success toast, no generic "Error loading".
    const errToast = page.locator('#toast-container .toast.error');
    await expect(errToast).toContainText('Animal saved, but its pedigree could not be loaded');
    await expect(page.locator('#toast-container .toast.success')).toHaveCount(0);
    await expect(page.locator('#toast-container .toast', { hasText: 'Error loading' })).toHaveCount(0);

    // Left create mode; form cleared; new row still selected for retry.
    await expect(page.locator('#add-animal-view')).not.toBeVisible();
    await expect(page.locator('#new-animal-id')).toHaveValue('');
    await expect(page.locator('.animal-list-item.selected', { hasText: 'Partial Win' })).toBeVisible();
    await expect(page.locator('#pedigree-title')).toContainText('could not be loaded');
    expect(posts).toBe(1);
  });

  // ISSUE-002: item routes (details / pedigree / offspring) reachable from UI.
  test('row click -> pedigree; pencil -> populated details; notes roundtrip', async ({ page, api }) => {
    const type = await api.createType();
    const dam = await api.createAnimal({ type_id: type.id, gender: 'female', name: 'Dam A', date_of_birth: '2019-01-05' });
    const kid = await api.createAnimal({ type_id: type.id, gender: 'female', name: 'Kid B', mother_id: dam.id, date_of_birth: '2021-03-04' });

    await page.goto('/');
    await gotoTab(page, type.name);

    // Row click loads pedigree.
    await selectAnimalRow(page, 'Kid B');
    await expect(page.locator('#pedigree-title')).toContainText('Kid B');
    await expect(page.locator('#pedigree-tree')).toContainText('Dam A');

    // Pencil opens populated details.
    await page.locator('.animal-list-item', { hasText: 'Kid B' }).locator('.animal-details-btn').click();
    await expect(page.locator('#details-view')).toBeVisible();
    await expect(page.locator('#animal-id')).toHaveValue(kid.identifier);
    await expect(page.locator('#animal-dob')).toHaveValue('2021-03-04');
    await expect(page.locator('#animal-mother')).toHaveValue(String(dam.id));

    // Notes round trip.
    await page.locator('#animal-notes').fill('note-xyz');
    await page.locator('#save-details-btn').click();
    await expect(page.locator('#toast-container .toast.success')).toBeVisible();
    const reloaded = await api.getAnimal(kid.id);
    expect(reloaded.notes).toBe('note-xyz');
  });

  test('offspring list renders and links work', async ({ page, api }) => {
    const type = await api.createType();
    const dam = await api.createAnimal({ type_id: type.id, gender: 'female', name: 'Mum', date_of_birth: '2018-02-02' });
    await api.createAnimal({ type_id: type.id, gender: 'male', name: 'Kidlet', mother_id: dam.id, date_of_birth: '2021-02-02' });

    await page.goto('/');
    await gotoTab(page, type.name);
    await page.locator('.animal-list-item', { hasText: 'Mum' }).locator('.animal-details-btn').click();
    await expect(page.locator('#offspring-list')).toContainText('Kidlet');
  });
});
