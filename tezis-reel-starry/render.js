// node render_captions.js <out_dir> <frames> [fps] -> PNG с прозрачным фоном на каждый кадр
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [out, n, fps = 30] = [process.argv[2], +process.argv[3], +(process.argv[4] || 30)];
  const only = process.argv[5] ? process.argv[5].split(',').map(Number) : null;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, 'reel.html'));
  await p.evaluate(() => document.fonts.ready);
  const frames = only ? only.map(t => Math.round(t * fps)) : [...Array(n).keys()];
  for (const i of frames) {
    await p.evaluate(t => window.render(t), i / fps);
    await p.locator('#s').screenshot({ path: path.join(out, `${String(i).padStart(5, '0')}.png`), omitBackground: true });
  }
  await b.close();
  console.log('frames', frames.length);
})();
