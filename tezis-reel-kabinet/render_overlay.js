// node render_overlay.js work/ov.json -> PNG с прозрачным фоном для каждой надписи
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, 'overlay.html'));
  await p.evaluate(() => document.fonts.ready);
  for (const j of jobs) {
    await p.evaluate(o => window.show(o), j.show);
    await p.evaluate(() => Promise.all([...document.images].map(i => i.complete ? 1 : new Promise(r => i.onload = r))));
    await p.locator('#s').screenshot({ path: j.f, omitBackground: true });
  }
  await b.close();
  console.log('overlays', jobs.length);
})();
