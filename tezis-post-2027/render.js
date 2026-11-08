// node render.js -> tezis_post_2027_1..7.png (2160x2700)
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 2 });
  p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto('file://' + path.join(__dirname, 'carousel.html'));
  await p.waitForFunction(() => window.READY);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  const s = await p.$$('section.s');
  for (let i = 0; i < s.length; i++) await s[i].screenshot({ path: path.join(__dirname, `tezis_post_2027_${i + 1}.png`) });
  await b.close();
  console.log(s.length);
})();
