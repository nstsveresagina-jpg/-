// node render.js -> tezis_reels_cover_idealno.png (2160x3840) + preview_grid.jpg кроп 3:4
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 2 });
  await p.goto('file://' + path.join(__dirname, 'cover.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  await p.locator('section.s').screenshot({ path: path.join(__dirname, 'tezis_reels_cover_idealno.png') });
  await b.close();
})();
