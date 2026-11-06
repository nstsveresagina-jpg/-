// Рисует пустую комнату в перспективе на canvas: drawRoom(canvas, opts)
// Все картинки поста рисуются этим кодом, сторонние изображения не используются.
(function () {
  const BASE = { wall: '#E8DED2', ceil: '#F1EBE3' };
  const hex = c => {
    if (c.startsWith('rgb')) return c.match(/[\d.]+/g).slice(0, 3).map(Number);
    c = c.replace('#', ''); return [0, 2, 4].map(i => parseInt(c.substr(i, 2), 16));
  };
  const rgb = (a, al = 1) => `rgba(${a.map(v => Math.round(Math.max(0, Math.min(255, v)))).join(',')},${al})`;
  const shade = (c, k) => { const a = hex(c); return rgb(k <= 1 ? a.map(v => v * k) : a.map(v => v + (255 - v) * (k - 1))); };
  const lerp = (a, b, t) => a + (b - a) * t;

  function drawRoom(cv, o = {}) {
    const ctx = cv.getContext('2d');
    const W = cv.width, H = cv.height;
    const bx1 = W * 0.21, bx2 = W * 0.79, by1 = H * 0.18, by2 = H * 0.69;
    const L = (t, v) => [lerp(0, bx1, t), lerp(lerp(0, by1, t), lerp(H, by2, t), v)];
    const R = (t, v) => [lerp(W, bx2, t), lerp(lerp(0, by1, t), lerp(H, by2, t), v)];
    const C = (t, u) => [lerp(lerp(0, W, u), lerp(bx1, bx2, u), t), lerp(0, by1, t)];
    const F = (t, u) => [lerp(lerp(0, W, u), lerp(bx1, bx2, u), t), lerp(H, by2, t)];
    const B = (u, v) => [lerp(bx1, bx2, u), lerp(by1, by2, v)];
    const path = pts => { ctx.beginPath(); pts.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.closePath(); };
    const poly = (pts, fill) => { path(pts); ctx.fillStyle = fill; ctx.fill(); };
    const clip = (pts, fn) => { ctx.save(); path(pts); ctx.clip(); fn(); ctx.restore(); };
    const s = W / 600; // масштаб толщин

    const wall = o.wall || BASE.wall;
    const col = { ceil: o.ceil || (o.wall && !o.lightCeil ? shade(o.wall, 1.12) : BASE.ceil), back: o.back || wall, left: o.left || wall, right: o.right || wall };
    const Q = {
      ceil: [[0, 0], [W, 0], [bx2, by1], [bx1, by1]],
      left: [[0, 0], [bx1, by1], [bx1, by2], [0, H]],
      right: [[W, 0], [W, H], [bx2, by2], [bx2, by1]],
      back: [[bx1, by1], [bx2, by1], [bx2, by2], [bx1, by2]],
      floor: [[0, H], [W, H], [bx2, by2], [bx1, by2]],
    };
    // поверхности с мягкой светотенью
    const grad = (x0, y0, x1, y1, stops) => { const g = ctx.createLinearGradient(x0, y0, x1, y1); stops.forEach(([p, c]) => g.addColorStop(p, c)); return g; };
    poly(Q.ceil, grad(0, 0, 0, by1, [[0, shade(col.ceil, 0.9)], [1, shade(col.ceil, 1.0)]]));
    poly(Q.left, grad(0, 0, bx1, 0, [[0, shade(col.left, 0.8)], [1, shade(col.left, 0.9)]]));
    poly(Q.right, grad(W, 0, bx2, 0, [[0, shade(col.right, 0.88)], [1, shade(col.right, 0.97)]]));
    poly(Q.back, grad(bx1, by1, bx2, by2, [[0, shade(col.back, 1.0)], [1, shade(col.back, 0.94)]]));

    // частичная окраска
    const accent = o.accent || '#6B4535';
    if (o.band) { // нижняя полоса по периметру
      const v = 0.72;
      poly([B(0, v), B(1, v), B(1, 1), B(0, 1)], shade(accent, 0.97));
      poly([L(0, v), L(1, v), L(1, 1), L(0, 1)], shade(accent, 0.82));
      poly([R(0, v), R(1, v), R(1, 1), R(0, 1)], shade(accent, 0.9));
    }
    if (o.panel) poly([B(0.2, 0.12), B(0.8, 0.12), B(0.8, 1), B(0.2, 1)], o.panel);
    if (o.stripesAll) { // вертикальные полосы на всех стенах
      const n = 18;
      for (let i = 0; i < n; i += 2) {
        poly([B(i / n, 0), B((i + 1) / n, 0), B((i + 1) / n, 1), B(i / n, 1)], shade(accent, 0.98));
      }
      const m = 22;
      for (let i = 0; i < m; i += 2) {
        const t0 = i / m, t1 = (i + 1) / m;
        poly([L(t0, 0), L(t1, 0), L(t1, 1), L(t0, 1)], shade(accent, 0.84));
        poly([R(t0, 0), R(t1, 0), R(t1, 1), R(t0, 1)], shade(accent, 0.92));
      }
    }

    // узоры на задней стене
    const bw = bx2 - bx1, bh = by2 - by1;
    if (o.pattern) clip(Q.back, () => {
      const p = o.pattern, a = o.patColor || accent;
      const [x0, y0] = B(0.1, 0.08), [x1, y1] = B(0.9, 1);
      const pw = x1 - x0, ph = y1 - y0;
      ctx.save(); ctx.beginPath(); ctx.rect(x0, y0, pw, ph); ctx.clip();
      const bg = o.patBg; if (bg) { ctx.fillStyle = bg; ctx.fillRect(x0, y0, pw, ph); }
      ctx.fillStyle = a;
      if (p === 'vlines' || p === 'slats') {
        const n = p === 'slats' ? 16 : 9;
        ctx.fillStyle = shade(a, 0.9); ctx.fillRect(x0, y0, pw, ph);
        for (let i = 0; i < n; i++) {
          const x = x0 + pw * (i + 0.5) / n, w = pw / n * (p === 'slats' ? 0.62 : 0.14);
          ctx.fillStyle = grad(x - w / 2, 0, x + w / 2, 0, [[0, shade(a, 1.08)], [0.5, shade(a, 1.0)], [1, shade(a, 0.78)]]);
          ctx.fillRect(x - w / 2, y0, w, ph);
          ctx.fillStyle = 'rgba(0,0,0,.18)'; ctx.fillRect(x + w / 2, y0, 2 * s, ph);
        }
      } else if (p === 'hlines') {
        ctx.fillRect(x0, y0, pw, ph);
        for (let i = 1; i < 6; i++) {
          const y = y0 + ph * i / 6;
          ctx.fillStyle = 'rgba(0,0,0,.28)'; ctx.fillRect(x0, y, pw, 2.5 * s);
          ctx.fillStyle = 'rgba(255,255,255,.18)'; ctx.fillRect(x0, y + 2.5 * s, pw, 1.5 * s);
        }
      } else if (p === 'wide' || p === 'narrow') {
        const n = p === 'wide' ? 7 : 25;
        for (let i = 0; i < n; i += 2) ctx.fillRect(x0 + pw * i / n, y0, pw / n, ph);
      } else if (p === 'diag') {
        ctx.save(); ctx.translate(x0, y0); ctx.rotate(-Math.PI / 4.2);
        const st = pw / 4.2;
        for (let i = -6; i < 8; i += 2) ctx.fillRect(i * st * 0.5, -ph * 2, st * 0.5, ph * 4);
        ctx.restore();
      } else if (p === 'shapes') {
        const r = ph * 0.34;
        ctx.beginPath(); ctx.arc(x0 + pw * 0.3, y1, r, Math.PI, 0); ctx.fill();
        ctx.beginPath(); ctx.moveTo(x1, y0); ctx.lineTo(x1, y1); ctx.lineTo(x1 - r * 0.9, y1); ctx.arc(x1, y1 - ph * 0.42, r * 0.9, Math.PI, Math.PI * 1.5); ctx.closePath(); ctx.fill();
        ctx.beginPath(); ctx.arc(x0 + pw * 0.62, y0 + ph * 0.4, r * 0.42, 0, Math.PI * 2); ctx.fill();
      } else if (p === 'small') {
        const cs = pw / 10;
        for (let j = 0; j * cs * 0.9 < ph + cs; j++) for (let i = 0; i < 11; i++) {
          const x = x0 + i * cs + (j % 2 ? cs / 2 : 0), y = y0 + j * cs * 0.9;
          ctx.save(); ctx.translate(x, y); ctx.rotate((i + j) % 2 ? 0.5 : -0.5);
          ctx.beginPath(); ctx.ellipse(0, -cs * 0.14, cs * 0.09, cs * 0.2, 0, 0, Math.PI * 2); ctx.fill();
          ctx.beginPath(); ctx.ellipse(-cs * 0.14, cs * 0.06, cs * 0.07, cs * 0.15, -1, 0, Math.PI * 2); ctx.fill();
          ctx.beginPath(); ctx.ellipse(cs * 0.14, cs * 0.06, cs * 0.07, cs * 0.15, 1, 0, Math.PI * 2); ctx.fill();
          ctx.restore();
        }
      } else if (p === 'mould') {
        ctx.fillRect(x0, y0, pw, ph);
        const n = 3, g = pw * 0.05, fw = (pw - g * (n + 1)) / n;
        for (let i = 0; i < n; i++) {
          const fx = x0 + g + i * (fw + g), fy = y0 + ph * 0.1, fh = ph * 0.8;
          ctx.lineWidth = 3 * s; ctx.strokeStyle = 'rgba(0,0,0,.25)'; ctx.strokeRect(fx + 2 * s, fy + 2 * s, fw, fh);
          ctx.strokeStyle = shade(a, 1.18); ctx.strokeRect(fx, fy, fw, fh);
        }
      } else if (p === 'mirror') {
        const off = document.createElement('canvas'); off.width = Math.round(pw); off.height = Math.round(ph);
        drawRoom(off, { ...(o.mirrorOpts || {}), sun: false, noMirror: true });
        ctx.save(); ctx.translate(x0 + pw, y0); ctx.scale(-1, 1); ctx.drawImage(off, 0, 0, pw, ph); ctx.restore();
        ctx.fillStyle = 'rgba(200,214,220,.22)'; ctx.fillRect(x0, y0, pw, ph);
        for (let i = 0; i <= 4; i++) { ctx.fillStyle = 'rgba(70,70,70,.55)'; ctx.fillRect(x0 + pw * i / 4 - 1.5 * s, y0, 3 * s, ph); }
        ctx.fillStyle = 'rgba(255,255,255,.12)'; ctx.beginPath(); ctx.moveTo(x0 + pw * 0.15, y0); ctx.lineTo(x0 + pw * 0.3, y0); ctx.lineTo(x0 + pw * 0.05, y1); ctx.lineTo(x0 - pw * 0.1, y1); ctx.fill();
      }
      ctx.restore();
    });

    // окно на левой стене
    const win = [L(0.24, 0.22), L(0.6, 0.27), L(0.6, 0.7), L(0.24, 0.73)];
    const quad = (q, a, b, c, d) => { // точка внутри четырёхугольника
      const top = [lerp(q[0][0], q[1][0], a), lerp(q[0][1], q[1][1], a)], bot = [lerp(q[3][0], q[2][0], a), lerp(q[3][1], q[2][1], a)];
      return [lerp(top[0], bot[0], b), lerp(top[1], bot[1], b)];
    };
    const sub = (q, a0, b0, a1, b1) => [quad(q, a0, b0), quad(q, a1, b0), quad(q, a1, b1), quad(q, a0, b1)];
    poly([quad(win, -0.06, -0.04), quad(win, 1.06, -0.04), quad(win, 1.06, 1.04), quad(win, -0.06, 1.04)], 'rgba(0,0,0,.12)');
    poly(win, '#F6F4F0');
    const glass = sub(win, 0.1, 0.06, 0.9, 0.94);
    const gb = glass.map(p => p[1]);
    poly(glass, grad(0, Math.min(...gb), 0, Math.max(...gb), [[0, '#E4EEF2'], [0.55, '#EEF2EE'], [0.62, '#B9C79C'], [1, '#93A877']]));
    poly(sub(win, 0.47, 0.03, 0.53, 0.97), '#F6F4F0');
    poly(sub(win, 0.03, 0.4, 0.97, 0.45), '#F6F4F0');
    poly(sub(win, -0.08, 0.98, 1.08, 1.05), '#FBFAF7'); // подоконник

    // пол: паркет
    poly(Q.floor, grad(0, H, 0, by2, [[0, shade(o.floor || '#C9A27C', 1.0)], [1, shade(o.floor || '#C9A27C', 0.86)]]));
    clip(Q.floor, () => {
      ctx.lineWidth = 1.2 * s;
      for (let i = 1; i < 16; i++) {
        const u = i / 16; ctx.strokeStyle = 'rgba(95,62,38,.16)';
        ctx.beginPath(); ctx.moveTo(...F(0, u)); ctx.lineTo(...F(1, u)); ctx.stroke();
      }
      for (let k = 0; k < 40; k++) { // стыки досок
        const u = ((k * 7) % 16 + 0.0) / 16, t = ((k * 37) % 100) / 100;
        const a = F(t, u), b = F(t, u + 1 / 16);
        ctx.strokeStyle = 'rgba(95,62,38,.12)'; ctx.beginPath(); ctx.moveTo(...a); ctx.lineTo(...b); ctx.stroke();
      }
      ctx.fillStyle = grad(0, by2, 0, H, [[0, 'rgba(255,255,255,.12)'], [0.4, 'rgba(255,255,255,0)']]); ctx.fillRect(0, by2, W, H - by2);
    });
    if (o.door) { // проём в соседнюю комнату с тем же полом
      const d = [R(0.22, 0.24), R(0.62, 0.3), R(0.62, 1), R(0.22, 1)];
      poly(d, shade(BASE.wall, 0.72));
      clip(d, () => { poly([R(0.22, 0.84), R(0.62, 0.88), d[2], d[3]], '#C29C77'); });
      ctx.lineWidth = 5 * s; ctx.strokeStyle = '#F4F0EA'; path(d); ctx.stroke();
    }

    // солнечные пятна
    const sunA = o.sun === false ? 0 : (o.sunA || 0.32);
    if (sunA) {
      ctx.save(); ctx.filter = `blur(${3 * s}px)`; ctx.globalCompositeOperation = 'screen';
      const panes = (q, al, colr) => {
        [[0, 0], [1, 0], [0, 1], [1, 1]].forEach(([i, j]) => poly(sub(q, i * 0.52, j * 0.53, i * 0.52 + 0.46, j * 0.53 + 0.45), `rgba(${colr},${al})`));
      };
      panes([F(0.12, 0.2), F(0.5, 0.17), F(0.58, 0.5), F(0.16, 0.6)], sunA * 0.9, '255,236,200');
      panes([B(0.1, 0.36), B(0.42, 0.31), B(0.45, 0.78), B(0.12, 0.86)], sunA, '255,238,205');
      ctx.restore();
    }

    // плинтусы
    poly([B(0, 0.975), B(1, 0.975), B(1, 1), B(0, 1)], '#F6F3EE');
    poly([L(0, 0.965), L(1, 0.975), L(1, 1), L(0, 1)], '#EDE8E1');
    poly([R(0, 0.965), R(1, 0.975), R(1, 1), R(0, 1)], '#F3EFE9');

    // мягкие тени в углах
    ctx.save(); ctx.filter = `blur(${7 * s}px)`; ctx.lineWidth = 10 * s; ctx.strokeStyle = 'rgba(40,25,15,.14)';
    path(Q.back); ctx.stroke();
    [[[0, 0], [bx1, by1]], [[W, 0], [bx2, by1]], [[0, H], [bx1, by2]], [[W, H], [bx2, by2]]].forEach(([a, b]) => { ctx.beginPath(); ctx.moveTo(...a); ctx.lineTo(...b); ctx.stroke(); });
    ctx.restore();

    // шторы
    if (o.curtains) clip(Q.back, () => {
      const [x0, y0] = B(0, 0), [x1, y1] = B(1, 1), n = 26;
      for (let i = 0; i < n; i++) {
        const x = x0 + (x1 - x0) * i / n, w = (x1 - x0) / n;
        ctx.fillStyle = grad(x, 0, x + w, 0, [[0, 'rgba(255,255,255,.62)'], [0.5, 'rgba(255,255,255,.4)'], [1, 'rgba(225,215,200,.5)']]);
        ctx.fillRect(x, y0, w, y1 - y0);
      }
      ctx.fillStyle = 'rgba(80,70,60,.6)'; ctx.fillRect(x0, y0, x1 - x0, 3 * s);
    });

    // освещение
    const lt = o.light;
    if (lt && lt !== 'diffuse') { // приглушаем дневной свет, чтобы был виден искусственный
      const dark = lt === 'side' ? 0.1 : 0.26;
      ctx.fillStyle = `rgba(70,50,35,${dark})`; ctx.fillRect(0, 0, W, H);
    }
    const glow = (fn, blur, al = 1) => { ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = al; ctx.filter = `blur(${blur * s}px)`; fn(); ctx.restore(); };
    const warmC = '255,206,140';
    if (lt === 'cove' || o.cove) {
      const edge = () => { ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(bx1, by1); ctx.lineTo(bx2, by1); ctx.lineTo(W, 0); ctx.stroke(); };
      glow(() => { ctx.strokeStyle = `rgba(${warmC},.75)`; ctx.lineWidth = 80 * s; edge(); }, 40);
      glow(() => { ctx.strokeStyle = `rgba(${warmC},1)`; ctx.lineWidth = 30 * s; edge(); }, 16);
      glow(() => { ctx.strokeStyle = `rgba(${warmC},.9)`; ctx.lineWidth = 8 * s; edge(); }, 4);
      glow(() => { ctx.strokeStyle = 'rgba(255,240,215,1)'; ctx.lineWidth = 3 * s; edge(); }, 0.5);
    }
    const cone = (u, al, wide = 1) => {
      const [x, y] = B(u, 0.02), h = bh * 0.8, w = bw * 0.11 * wide;
      glow(() => {
        ctx.fillStyle = grad(0, y, 0, y + h, [[0, `rgba(${warmC},${al})`], [1, `rgba(${warmC},0)`]]);
        ctx.beginPath(); ctx.moveTo(x - w * 0.25, y); ctx.lineTo(x + w * 0.25, y); ctx.lineTo(x + w * 1.3, y + h); ctx.lineTo(x - w * 1.3, y + h); ctx.fill();
        ctx.fillStyle = `rgba(${warmC},${al * 0.8})`; ctx.beginPath(); ctx.ellipse(x, y + h * 0.42, w * 0.9, h * 0.3, 0, 0, Math.PI * 2); ctx.fill();
      }, 12);
      const [cx, cy] = C(0.85, u); ctx.fillStyle = '#2B2622'; ctx.fillRect(cx - 4 * s, cy - 2 * s, 8 * s, 12 * s);
    };
    if (lt === 'wash') [0.25, 0.5, 0.75].forEach(u => cone(u, 0.75));
    if (lt === 'accent') cone(0.62, 0.95, 1.2);
    if (lt === 'top') {
      const [cx, cy] = C(0.55, 0.5);
      glow(() => { ctx.fillStyle = `rgba(255,236,205,.55)`; ctx.beginPath(); ctx.ellipse(cx, cy + 40 * s, 230 * s, 150 * s, 0, 0, Math.PI * 2); ctx.fill(); }, 50);
      ctx.fillStyle = '#FFFDF8'; ctx.beginPath(); ctx.ellipse(cx, cy, 52 * s, 11 * s, 0, 0, Math.PI * 2); ctx.fill();
      glow(() => { ctx.fillStyle = 'rgba(255,245,225,1)'; ctx.beginPath(); ctx.ellipse(cx, cy, 60 * s, 16 * s, 0, 0, Math.PI * 2); ctx.fill(); }, 8);
    }
    if (lt === 'floor') {
      const strip = () => { ctx.beginPath(); ctx.moveTo(...B(0, 0.97)); ctx.lineTo(...B(1, 0.97)); ctx.stroke(); };
      glow(() => { ctx.strokeStyle = `rgba(${warmC},.7)`; ctx.lineWidth = 90 * s; strip(); }, 40);
      glow(() => { ctx.strokeStyle = `rgba(${warmC},1)`; ctx.lineWidth = 30 * s; strip(); }, 14);
      glow(() => { ctx.strokeStyle = 'rgba(255,235,200,1)'; ctx.lineWidth = 3 * s; strip(); }, 0.5);
    }
    if (lt === 'side') {
      ctx.save(); ctx.filter = `blur(${2 * s}px)`;
      [[0, 0], [1, 0], [0, 1], [1, 1]].forEach(([i, j]) => poly(sub([B(0.3, 0.12), B(0.75, 0.05), B(0.8, 0.85), B(0.33, 0.95)], i * 0.52, j * 0.53, i * 0.52 + 0.46, j * 0.53 + 0.45), 'rgba(255,226,170,.55)'));
      ctx.restore();
    }
    if (lt === 'warm') { ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = 'rgba(255,190,120,.42)'; ctx.fillRect(0, 0, W, H); ctx.restore(); glow(() => { ctx.fillStyle = 'rgba(255,200,130,.25)'; ctx.fillRect(0, 0, W, H); }, 0); }
    if (lt === 'cold') { ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = 'rgba(175,195,215,.6)'; ctx.fillRect(0, 0, W, H); ctx.restore(); glow(() => { ctx.fillStyle = 'rgba(200,215,230,.2)'; ctx.fillRect(0, 0, W, H); }, 0); }
    if (lt === 'diffuse') glow(() => { ctx.fillStyle = 'rgba(255,248,238,.18)'; ctx.fillRect(0, 0, W, H); }, 0);
  }
  window.drawRoom = drawRoom;
})();
