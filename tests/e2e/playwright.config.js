const { defineConfig, devices } = require('@playwright/test');
const path = require('path');
const os = require('os');

const ROOT = path.resolve(__dirname, '..', '..');
const E2E_DIR = process.env.E2E_DIR || path.join(os.tmpdir(), 'pedigree-e2e');
const PORT = process.env.E2E_PORT || '8001';
const BASE_URL = `http://localhost:${PORT}`;

const chrome = devices['Desktop Chrome'];

module.exports = defineConfig({
  testDir: __dirname,
  timeout: 30_000,
  retries: 0,
  workers: 1,
  reporter: [['list']],
  use: {
    baseURL: BASE_URL,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  webServer: {
    command: `env PORT=${PORT} DATABASE_URL=sqlite:///${E2E_DIR}/e2e.db LOG_FILE=${E2E_DIR}/app.log PYTHONDONTWRITEBYTECODE=1 "${ROOT}/venv/bin/python" -m src.app`,
    cwd: ROOT,
    url: `${BASE_URL}/health`,
    reuseExistingServer: false,
    timeout: 60_000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...chrome },
      testIgnore: /dates\.spec\.js/,
    },
    {
      name: 'tz-new-york',
      use: { ...chrome, timezoneId: 'America/New_York' },
      testMatch: /dates\.spec\.js/,
    },
    {
      name: 'tz-utc',
      use: { ...chrome, timezoneId: 'UTC' },
      testMatch: /dates\.spec\.js/,
    },
    {
      name: 'tz-kiritimati',
      use: { ...chrome, timezoneId: 'Pacific/Kiritimati' },
      testMatch: /dates\.spec\.js/,
    },
    {
      name: 'tz-pago-pago',
      use: { ...chrome, timezoneId: 'Pacific/Pago_Pago' },
      testMatch: /dates\.spec\.js/,
    },
  ],
});
