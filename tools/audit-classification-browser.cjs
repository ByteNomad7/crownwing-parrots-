/* Read-only mobile rendering audit across every real generated HTML route. */
const fs = require("node:fs");
const path = require("node:path");
const {execFileSync} = require("node:child_process");
const puppeteer = require("puppeteer-core");

function routes(directory, root = directory) {
  return fs.readdirSync(directory, {withFileTypes: true}).flatMap(entry => {
    const file = path.join(directory, entry.name);
    if (entry.isDirectory()) return routes(file, root);
    if (entry.name !== "index.html") return [];
    const relative = path.relative(root, directory);
    return [relative ? "/" + relative.split(path.sep).join("/") + "/" : "/"];
  });
}

(async () => {
  if (!process.env.REPLIT_DEV_DOMAIN) throw new Error("Running preview domain required");
  const origin = "https://" + process.env.REPLIT_DEV_DOMAIN;
  const browser = await puppeteer.launch({
    executablePath: execFileSync("which", ["chromium"], {encoding: "utf8"}).trim(),
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
  });
  const records = [];
  try {
    const page = await browser.newPage();
    await page.setViewport({width: 390, height: 900});
    let pageErrors = [];
    page.on("pageerror", error => pageErrors.push(error.message));
    for (const route of routes("dist").sort()) {
      pageErrors = [];
      try {
        const response = await page.goto(origin + route, {waitUntil: "load", timeout: 30000});
        await page.evaluate(() => Promise.race([
          document.fonts.ready, new Promise(resolve => setTimeout(resolve, 1500)),
        ]));
        const result = await page.evaluate(() => ({
          title: document.title,
          h1: [...document.querySelectorAll("main h1")].map(el => el.textContent.trim()),
          htmlLinks: document.querySelectorAll('main a[href]').length,
          overflow: document.documentElement.scrollWidth > window.innerWidth + 1,
          canonical: document.querySelector('link[rel="canonical"]')?.href,
          menuPresent: Boolean(document.querySelector("button.menu")),
          enhancedBudget: document.querySelector('[data-budget-form] button[type="submit"]')?.disabled === false,
          comparisonGroups: new Set([...document.querySelectorAll("#group-comparison [data-group]")]
            .filter(el => !el.hidden).map(el => el.dataset.group)).size,
        }));
        await page.click("button.menu");
        result.menuOpens = await page.$eval("nav", el => el.classList.contains("open"));
        records.push({route, status: response.status(), ...result, pageErrors: [...pageErrors]});
      } catch (error) {
        records.push({route, error: error.message, pageErrors: [...pageErrors]});
      }
    }
    fs.writeFileSync("seo/crownwing-mobile-rendering.json", JSON.stringify({
      checked_at: new Date().toISOString(), viewport: {width: 390, height: 900},
      environment: "HTTPS development proxy; not published-host or field CWV evidence",
      scope: "All routes: rendered title/H1/canonical, HTML links, horizontal containment, JavaScript errors and mobile navigation.",
      limits: "Not a full accessibility audit or interaction test for every gallery/form. Existing buyer-tools browser evidence covers both responsive sizes and no-JS safeguards.",
      pages: records,
    }, null, 2));
    const problems = records.filter(r => r.error || r.status !== 200 || r.overflow ||
      r.h1?.length !== 1 || !r.menuOpens || r.pageErrors?.length);
    console.log(JSON.stringify({routes: records.length, mobileProblems: problems}, null, 2));
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error); process.exitCode = 1;});