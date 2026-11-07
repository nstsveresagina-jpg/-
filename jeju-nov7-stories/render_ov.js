// Оверлеи для видео-сторис: прозрачный PNG 1080×1920 на каждую сторис (карточка, логотип, полароид)
const{chromium}=require('playwright');const path=require('path');const fs=require('fs');const d=__dirname;
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.join(d,'stories.html'));
const swap=JSON.parse(fs.readFileSync(path.join(d,'video_polaroids.json'),'utf8'));
await p.evaluate(sw=>{document.body.classList.add('ov');for(const [id,img] of Object.entries(sw)){const el=document.querySelector('#'+id+' .pol div');if(el)el.style.backgroundImage=`url(${img})`;}},swap);
await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
fs.mkdirSync(path.join(d,'ov'),{recursive:true});
const n=await p.$$eval('section.s',s=>s.length);
for(let i=1;i<=n;i++)await(await p.$('#s'+i)).screenshot({path:path.join(d,'ov',`ov_${i}.png`),omitBackground:true});await b.close();})();
