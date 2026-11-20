// Shared fixtures: API helper + auto-fail on API 5xx responses.
const { test: base, expect, request } = require('@playwright/test');

let counter = 0;
const unique = (prefix) => `${prefix}-${Date.now().toString(36)}-${++counter}`;

const test = base.extend({
  // Fail the test if any /api/ response is a 5xx.
  page: async ({ page }, use) => {
    const apiErrors = [];
    page.on('response', (r) => {
      if (r.url().includes('/api/') && r.status() >= 500) {
        apiErrors.push(`${r.status()} ${r.url()}`);
      }
    });
    await use(page);
    expect(apiErrors, 'API returned 5xx responses').toEqual([]);
  },

  api: async ({ baseURL }, use) => {
    const ctx = await request.newContext({ baseURL });
    const api = {
      baseURL,
      async createType(overrides = {}) {
        const res = await ctx.post('/api/v1/animal-types/', {
          data: { name: unique('type'), ...overrides },
        });
        expect(res.ok()).toBeTruthy();
        return res.json();
      },
      async createAnimal(overrides) {
        const res = await ctx.post('/api/v1/animals/', {
          data: { identifier: unique('A'), ...overrides },
        });
        if (!res.ok()) {
          throw new Error(`createAnimal failed ${res.status()}: ${await res.text()}`);
        }
        return res.json();
      },
      async getAnimal(id) {
        const res = await ctx.get(`/api/v1/animals/${id}`);
        expect(res.ok()).toBeTruthy();
        return res.json();
      },
    };
    await use(api);
    await ctx.dispose();
  },
});

// Helpers usable inside tests.
async function gotoTab(page, typeName) {
  await page.locator('.animal-tabs .tab-btn', { hasText: typeName }).click();
}

async function selectAnimalRow(page, animalName) {
  await page.locator('.animal-list-item', { hasText: animalName })
    .locator('.animal-select-btn')
    .click();
}

module.exports = { test, expect, unique, gotoTab, selectAnimalRow };
