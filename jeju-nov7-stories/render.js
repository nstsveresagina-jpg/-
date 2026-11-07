const{chromium}=require('playwright');const path=require('path');const d=__dirname;
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.join(d,'stories.html'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
const n=await p.$$eval('section.s',s=>s.length);
for(let i=1;i<=n;i++)await(await p.$('#s'+i)).screenshot({path:path.join(d,`story_${i}.png`)});await b.close();})();
