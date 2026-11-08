// Прозрачные оверлеи 1080×1920 для видео-сторис: карточка и логотип
const{chromium}=require('playwright');const path=require('path');const fs=require('fs');const d=__dirname;
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.join(d,'stories.html'));await p.evaluate(()=>document.body.classList.add('ov'));
await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);fs.mkdirSync(path.join(d,'ov'),{recursive:true});
const n=await p.$$eval('section.s',s=>s.length);
for(let i=1;i<=n;i++)await(await p.$('#s'+i)).screenshot({path:path.join(d,'ov',`ov_${i}.png`),omitBackground:true});await b.close();})();
