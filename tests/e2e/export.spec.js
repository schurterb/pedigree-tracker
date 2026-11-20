const { test, expect, gotoTab } = require('./fixtures');

test.describe('export', () => {
  test('PNG, PDF and JSON exports produce downloads', async ({ page, api }) => {
    const type = await api.createType();
    const dam = await api.createAnimal({ type_id: type.id, gender: 'female', name: 'Exp Dam', date_of_birth: '2019-01-01' });
    const kid = await api.createAnimal({ type_id: type.id, gender: 'female', name: 'Exp Kid', mother_id: dam.id, date_of_birth: '2021-01-01' });

    await page.goto('/');
    await gotoTab(page, type.name);
    await page.locator('.animal-list-item', { hasText: 'Exp Kid' }).locator('.animal-select-btn').click();
    await expect(page.locator('#pedigree-tree')).toContainText('Exp Dam');

    const openExportModal = async () => {
      await page.locator('#export-pedigree').click();
      await expect(page.locator('#export-modal')).toBeVisible();
    };
    await openExportModal();

    // JSON export — validate content matches the API payload.
    const [jsonDownload] = await Promise.all([
      page.waitForEvent('download'),
      page.locator('#export-json-btn').click(),
    ]);
    expect(jsonDownload.suggestedFilename()).toMatch(/\.json$/);
    const fs = require('fs');
    const jsonText = fs.readFileSync(await jsonDownload.path(), 'utf8');
    const parsed = JSON.parse(jsonText);
    expect(parsed.name).toBe('Exp Kid');

    // PNG + PDF download events fire (each export closes the modal).
    for (const btn of ['#export-png-btn', '#export-pdf-btn']) {
      await openExportModal();
      const [dl] = await Promise.all([
        page.waitForEvent('download', { timeout: 20_000 }),
        page.locator(btn).click(),
      ]);
      expect(dl.suggestedFilename()).toMatch(/\.(png|pdf)$/);
    }
  });
});
