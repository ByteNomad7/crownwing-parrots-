/* Check real photo loading and group navigation on desktop and phone. */
const assert = require('node:assert/strict');
const puppeteer = require('puppeteer-core');
const {execFileSync} = require('node:child_process');

(async () => {
  assert(process.env.REPLIT_DEV_DOMAIN, 'Running preview required');
  const origin = 'https://' + process.env.REPLIT_DEV_DOMAIN;
  const browser = await puppeteer.launch({
    executablePath: execFileSync('which', ['chromium'], {encoding: 'utf8'}).trim(),
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
  });
  const results = [];
  try {
    for (const width of [1280, 390]) {
      const page = await browser.newPage();
      await page.setViewport({width, height: 900});
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      const response = await page.goto(origin + '/', {waitUntil: 'networkidle2'});
      assert([200, 304].includes(response.status()));
      assert.equal(await page.$$eval('h1', nodes => nodes.length), 1);
      assert.equal(await page.$$eval('.hp-story', nodes => nodes.length), 3);
      assert.equal(await page.$$eval('.species-grid a', nodes => nodes.length), 8);
      const count = await page.$$eval('main img', nodes => nodes.length);
      assert(count >= 14, 'Photos must appear beyond the original species cards');
      for (let index = 0; index < count; index++) {
        await page.evaluate(i => document.querySelectorAll('main img')[i].scrollIntoView({block: 'center'}), index);
        await page.waitForFunction(i => {
          const image = document.querySelectorAll('main img')[i];
          return image.complete && image.naturalWidth > 0;
        }, {timeout: 15000}, index);
      }
      const layout = await page.evaluate(() => ({
        overflow: document.documentElement.scrollWidth - innerWidth,
        contained: [...document.querySelectorAll('.hp-photo-link')].every(node => {
          const rect = node.getBoundingClientRect();
          return rect.width > 0 && rect.left >= 0 && rect.right <= innerWidth + 1;
        }),
      }));
      assert(layout.overflow <= 2, JSON.stringify(layout));
      assert(layout.contained, 'New photos must fit the viewport');
      const links = await page.$$eval('.hp-photo-link, .species-grid a', nodes => nodes.map(node => node.href));
      const statuses = await page.evaluate(async urls =>
        Promise.all([...new Set(urls)].map(async url => [url, (await fetch(url)).status])), links);
      assert(statuses.every(([, status]) => status === 200), JSON.stringify(statuses));
      await page.$eval('.hp-photo-link', node => node.scrollIntoView({block: 'center'}));
      await Promise.all([page.waitForNavigation({waitUntil: 'load'}), page.click('.hp-photo-link')]);
      assert(new URL(page.url()).pathname === '/parrots/african-parrots/');
      assert.deepEqual(errors, []);
      results.push({width, loaded_photos: count, working_group_routes: statuses.length});
      await page.close();
    }
    console.log(JSON.stringify({homepage_photography: 'passed', results}));
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error); process.exitCode = 1;});