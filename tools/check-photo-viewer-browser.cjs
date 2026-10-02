/* Exercise displayed image pixels/currentSrc, not merely changing src attributes. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {execFileSync} = require('node:child_process');
const puppeteer = require('puppeteer-core');

function galleryRoutes(directory, root = directory) {
  return fs.readdirSync(directory, {withFileTypes: true}).flatMap(entry => {
    const file = path.join(directory, entry.name);
    if (entry.isDirectory()) return galleryRoutes(file, root);
    if (entry.name !== 'index.html' || !fs.readFileSync(file, 'utf8').includes('class="detail-gallery"')) return [];
    return ['/' + path.relative(root, directory).split(path.sep).join('/') + '/'];
  });
}

(async () => {
  assert(process.env.REPLIT_DEV_DOMAIN, 'Running preview domain required');
  const browser = await puppeteer.launch({
    executablePath: execFileSync('which', ['chromium'], {encoding: 'utf8'}).trim(),
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
  });
  let selections = 0;
  const routes = galleryRoutes('dist');
  assert(routes.length > 0);
  try {
    for (const width of [1280, 390]) {
      const page = await browser.newPage();
      await page.setViewport({width, height: 900});
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      for (const route of routes) {
        const response = await page.goto('https://' + process.env.REPLIT_DEV_DOMAIN + route, {waitUntil: 'load'});
        assert([200, 304].includes(response.status()), `Unexpected page response: ${response.status()}`);
        const photos = await page.$$eval('.detail-gallery [data-photo-src]', buttons => buttons.map(b => b.dataset.photoSrc));
        async function verify(index) {
          await page.waitForFunction(expected => {
            const images = [document.querySelector('#photo-dialog img'), document.querySelector('.gallery-main img')];
            return images.every(img => img.complete && img.naturalWidth > 0 &&
              new URL(img.currentSrc).pathname === expected);
          }, {timeout: 15000}, photos[index]);
          const state = await page.evaluate(() => ({
            open: document.querySelector('#photo-dialog').open,
            caption: document.querySelector('.photo-dialog-caption').textContent,
            srcsets: [document.querySelector('#photo-dialog img'), document.querySelector('.gallery-main img')].map(i => i.getAttribute('srcset')),
          }));
          assert(state.open, route);
          assert(state.caption.includes(`Photo ${index + 1} of ${photos.length}`), route);
          assert(state.srcsets.every(value => value === null), route);
          selections++;
        }
        // Select every thumbnail, including the default-expanded extra collection.
        for (let index = 0; index < photos.length; index++) {
          await page.evaluate(() => document.querySelector('#photo-dialog').close());
          const buttons = await page.$$('.detail-gallery [data-photo-src]');
          await buttons[index].click();
          await verify(index);
        }
        // Last -> first and first -> last wrapping, keyboard navigation and reopen.
        await page.click('#photo-dialog .photo-next');
        await verify(0);
        await page.click('#photo-dialog .photo-prev');
        await verify(photos.length - 1);
        await page.keyboard.press('ArrowRight');
        await verify(0);
        await page.keyboard.press('ArrowLeft');
        await verify(photos.length - 1);
        await page.keyboard.press('Escape');
        assert.equal(await page.$eval('#photo-dialog', d => d.open), false);
        await page.click('.gallery-main');
        await verify(photos.length - 1);
        await page.click('#photo-dialog .close');
        assert.equal(await page.$eval('#photo-dialog', d => d.open), false);
      }
      assert.deepEqual(errors, []);
      await page.close();
    }
    console.log(JSON.stringify({gallery_pages: routes.length, viewport_widths: [1280, 390], verified_selections: selections, photo_viewer: 'passed'}));
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error); process.exitCode = 1;});