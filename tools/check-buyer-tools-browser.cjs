/* Exercise actual controls, mobile navigation, and no-JS content in Chromium. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const {execFileSync} = require("node:child_process");
const puppeteer = require("puppeteer-core");

(async () => {
  const origin = `https://${process.env.REPLIT_DEV_DOMAIN}`;
  if (!process.env.REPLIT_DEV_DOMAIN) throw new Error("Preview domain unavailable");
  const browser = await puppeteer.launch({
    executablePath: execFileSync("which", ["chromium"], {encoding: "utf8"}).trim(),
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
  });
  const results = [];
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    for (const width of [1366, 390]) {
      await page.setViewport({width, height: 950});
      await page.goto(origin + "/guides/choosing-a-parrot/", {waitUntil: "networkidle0", timeout: 45000});
      await page.select("#comparison-first", "macaws");
      await page.select("#comparison-second", "macaws");
      await page.click("[data-comparison-show]");
      assert.match(await page.$eval("[data-comparison-message]", el => el.textContent), /different/i);
      await page.select("#comparison-second", "conures");
      await page.click("[data-comparison-show]");
      const shown = await page.$$eval("#group-comparison [data-group]", cells =>
        [...new Set(cells.filter(el => !el.hidden).map(el => el.dataset.group))].sort());
      assert.deepEqual(shown, ["conures", "macaws"]);
      await page.click("[data-comparison-reset]");
      assert.equal(await page.$$eval("#group-comparison [data-group]", cells =>
        new Set(cells.filter(el => !el.hidden).map(el => el.dataset.group)).size), 8);
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1), "Comparison causes page overflow");

      await page.goto(origin + "/guides/parrot-ownership-costs/", {waitUntil: "networkidle0", timeout: 45000});
      const values = {purchase: "1000", cage: "400", initialEquipment: "100", transport: "50",
        food: "30", toys: "20", veterinarySaving: "40", insurance: "10", emergencyReserve: "500"};
      for (const [name, value] of Object.entries(values)) {
        await page.$eval(`[name="${name}"]`, (el, value) => { el.value = value; }, value);
      }
      await page.$eval("[data-budget-form]", el => el.requestSubmit());
      await page.waitForFunction(() => !document.querySelector("[data-budget-results]").hidden);
      const amounts = await page.$$eval("[data-result]", els =>
        Object.fromEntries(els.map(el => [el.dataset.result, el.textContent])));
      assert.equal(amounts.setupSpend, "£1,550.00");
      assert.equal(amounts.monthlyOngoing, "£100.00");
      assert.equal(amounts.firstYearPlannedSpend, "£2,750.00");
      assert.equal(amounts.startingCash, "£2,050.00");
      assert.equal(amounts.emergencyReserve, "£500.00");
      await page.$eval("[data-budget-form]", el => el.reset());
      assert(await page.$eval("[data-budget-results]", el => el.hidden));
      await page.$eval("[data-budget-form]", el => el.requestSubmit());
      assert(await page.$eval("[data-budget-results]", el => el.hidden), "Blank inputs yielded a misleading total");
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1), "Budget causes page overflow");
      results.push({width, comparison: "passed", budget: "passed", overflow: "none"});
    }
    const plain = await browser.newPage();
    await plain.setJavaScriptEnabled(false);
    await plain.goto(origin + "/guides/choosing-a-parrot/", {waitUntil: "networkidle0", timeout: 45000});
    assert.equal(await plain.$$eval("#group-comparison [data-group]", cells =>
      new Set(cells.filter(el => !el.hidden).map(el => el.dataset.group)).size), 8);
    await plain.goto(origin + "/guides/parrot-ownership-costs/", {waitUntil: "networkidle0", timeout: 45000});
    assert(await plain.$eval('[data-budget-form] button[type="submit"]', el => el.disabled));
    let navigations = 0;
    plain.on("request", request => { if (request.isNavigationRequest()) navigations++; });
    await plain.type("#budget-purchase", "1000");
    await plain.keyboard.press("Enter");
    await new Promise(resolve => setTimeout(resolve, 300));
    assert.equal(navigations, 0, "No-JS budget leaked estimates through a GET submission");
    assert.equal(errors.length, 0, `Browser errors: ${errors.join("; ")}`);
    fs.writeFileSync("seo/buyer-tools-browser.json", JSON.stringify({
      verified_at: new Date().toISOString(), environment: "running preview via HTTPS proxy",
      results, no_javascript_comparison: "all eight readable", page_errors: errors,
      no_javascript_budget: "submission disabled; Enter sends no request",
      fixture_note: "Test amounts only; never displayed as retailer prices.",
    }, null, 2));
    console.log("Buyer browser tests passed: comparison, calculator, reset, missing inputs, no-JS and mobile containment.");
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });