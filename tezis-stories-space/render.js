// node render.js -> tezis_story_space_1..7.png (2160x3840)
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 2 });
  await p.goto('file://' + path.join(__dirname, 'stories.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  const s = await p.$$('section.s');
  for (let i = 0; i < s.length; i++) await s[i].screenshot({ path: path.join(__dirname, `tezis_story_space_${i + 1}.png`) });
  await b.close();
  console.log(s.length);
})();
