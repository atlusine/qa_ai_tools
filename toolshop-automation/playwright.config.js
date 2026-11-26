const path = require("path");
const { defineConfig, devices } = require("@playwright/test");

require("dotenv").config({ path: path.resolve(__dirname, ".env") });

module.exports = defineConfig({
  testDir: "./tests",
  outputDir: "./test-results",
  timeout: 90 * 1000,
  expect: { timeout: 15000 },
  fullyParallel: true,
  workers: process.env.CI ? 2 : 4,
  retries: 1,
  forbidOnly: true,
  reporter: process.env.CI
    ? [["list"], ["html", { outputFolder: "./report", open: "never" }], ["junit", { outputFile: "./test-reports/junit.xml" }]]
    : [["list"], ["html", { outputFolder: "./report", open: "never" }]],
  use: {
    baseURL: process.env.BASE_URL || "https://practicesoftwaretesting.com",
    testIdAttribute: "data-test",
    actionTimeout: 15000,
    navigationTimeout: 60000,
    viewport: { width: 1280, height: 800 },
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    trace: "retain-on-failure",
  },
  projects: [{ name: "chrome", use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 800 } } }],
});
