# Reels renderer: "Рождество и Новый год на Бали" (JEJU TRIP), template of the Fukuok reels (../phuquoc-december)
# usage: python3 render.py <src_dir> <music.wav> <out.mp4> [--from SEC --to SEC] [--stills DIR]
import sys, os, math, random, subprocess, json, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('music'); ap.add_argument('out')
ap.add_argument('--from', dest='t_from', type=float, default=0)
ap.add_argument('--to', dest='t_to', type=float, default=None)
ap.add_argument('--stills', default=None, help='dump every Nth frame as jpg into this dir')
ap.add_argument('--stills-every', type=int, default=15)
A = ap.parse_args()

HERE = os.path.dirname(os.path.abspath(__file__))
FPS, W, H = 30, 1080, 1920
WORK_H = 2112                      # working height (10% zoom headroom)
WORK_W = WORK_H * 9 // 16          # 1188
P, PH = 0.43460, 0.0               # beat period / phase of music.wav (138 BPM, cut on a beat); 12-beat blocks
def beat(k): return PH + k * P

DUR = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', A.music]))
NFR = int(DUR * FPS)

F_HEAD = os.path.join(HERE, 'fonts/AdvakenSans.otf')     # bold — headings
if not os.path.exists(F_HEAD): F_HEAD = os.path.join(HERE, 'fonts/Unbounded-ExtraBold.ttf')
F_BODY = os.path.join(HERE, 'fonts/Comfortaa-Light.ttf')  # thin — body text
ORANGE, RED = (247, 165, 32), (232, 87, 42)
NAVY, CREAM = (30, 43, 60), (251, 246, 236)

# ---------------------------------------------------------------- edit list
G_SOFT = dict(sat=1.06, con=1.03, bri=0.01, gam=1.02, vib=0.10)
G_STD  = dict(sat=1.18, con=1.06, bri=0.015, gam=1.03, vib=0.20)
G_PUSH = dict(sat=1.30, con=1.10, bri=0.02, gam=1.06, vib=0.30)
G_WARM = dict(sat=1.10, con=1.02, bri=0.02, gam=1.05, vib=0.12)
G_NIGHT = dict(sat=1.20, con=1.00, bri=0.02, gam=1.12, vib=0.20)
G_PINK = dict(sat=1.12, con=1.04, bri=0.02, gam=1.04, vib=0.14)
SLOTS = [
    # 0-10 hook: БАЛИ / РОЖДЕСТВО И НОВЫЙ ГОД
    dict(k=0,  src='diamond_beach',    ss=2.0,  z=(1.00, 1.06), g=G_STD),
    dict(k=3,  src='jungle_mist',      ss=4.0,  z=(1.00, 1.05), g=G_STD, punch=0.16),
    dict(k=5,  src='beach_club',       ss=2.0,  z=(1.00, 1.05), g=G_WARM),
    dict(k=7,  src='fireworks_sea',    ss=5.0,  z=(1.00, 1.05), g=G_NIGHT),
    # 10-18 Ubud
    dict(k=10, src='rice_terrace',     ss=1.0,  z=(1.00, 1.05), g=G_STD, punch=0.14),
    dict(k=12, src='waterfall_aerial', ss=2.0,  z=(1.00, 1.04), g=G_STD),
    dict(k=14, src='monkeys_temple',   ss=3.0,  z=(1.00, 1.04), g=G_STD),
    dict(k=16, src='jungle_swing',     ss=1.0,  z=(1.00, 1.04), g=G_STD),
    # 18-24 volcano sunrise
    dict(k=18, src='batur_clouds',     ss=0.5,  z=(1.00, 1.05), g=G_WARM, punch=0.14),
    dict(k=20, src='jeep_sunrise',     ss=5.0,  z=(1.00, 1.04), g=G_WARM),
    dict(k=22, src='batur_dawn',       ss=12.0, z=(1.00, 1.04), g=G_WARM),
    # 24-32 Nusa Penida + snorkeling
    dict(k=24, src='kelingking',       ss=1.0,  z=(1.00, 1.05), g=G_STD, punch=0.14),
    dict(k=26, src='waves_aerial',     ss=2.0,  z=(1.00, 1.04), g=G_STD),
    dict(k=28, src='manta',            ss=1.5,  z=(1.00, 1.04), g=G_STD),
    dict(k=30, src='nusa_rocks',       ss=3.0,  z=(1.00, 1.04), g=G_STD),
    # 32-38 SPA and traditions
    dict(k=32, src='flower_bath',      ss=2.5,  z=(1.00, 1.05), g=G_WARM, punch=0.12),
    dict(k=34, src='ceremony_women',   ss=17.0, z=(1.00, 1.04), g=G_STD),
    dict(k=36, src='lake_temple',      ss=0.5,  z=(1.00, 1.04), g=G_STD),
    # 38-44 adventures
    dict(k=38, src='surf_girl',        ss=20.0, z=(1.00, 1.04), g=G_STD, punch=0.12),
    dict(k=40, src='beach_club',       ss=7.0,  z=(1.00, 1.04), g=G_WARM),
    dict(k=42, src='surf_wave',        ss=5.0,  z=(1.00, 1.04), g=G_STD),
    # 44-50 Christmas + New Year
    dict(k=44, src='palm_lights',      ss=4.0,  z=(1.00, 1.05), g=G_NIGHT, punch=0.12),
    dict(k=47, src='fireworks_pink',   ss=1.0,  z=(1.00, 1.05), g=G_NIGHT),
    # 50-59 price and call to action
    dict(k=50, src='sunset_waves',     ss=3.0,  z=(1.00, 1.05), g=G_WARM, punch=0.12),
    dict(k=54, src='sunset_palms',     ss=4.0,  z=(1.00, 1.05), g=G_WARM),
    # 59-end logo
    dict(k=59, src='fireworks_gold',   ss=10.0, z=(1.00, 1.04), g=G_NIGHT, punch=0.16),
]
for i, s in enumerate(SLOTS):
    s['f0'] = int(round(beat(s['k']) * FPS)) if i else 0
for i, s in enumerate(SLOTS):
    s['f1'] = SLOTS[i + 1]['f0'] if i + 1 < len(SLOTS) else NFR

FLASH = [(beat(3), 0.60, 0.18), (beat(10), 0.45, 0.14), (beat(44), 0.40, 0.14), (beat(59), 0.75, 0.30)]
LEAKS = [(beat(18), 0.35), (beat(32), 0.35), (beat(50), 0.40)]

# ---------------------------------------------------------------- helpers
def ease_out(x):   x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_inout(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def ease_back(x, s=1.9):
    x = min(max(x, 0), 1); x -= 1; return x * x * ((s + 1) * x + s) + 1
def lerp(a, b, x): return a + (b - a) * x

_probe = {}
def probe(path):
    if path not in _probe:
        o = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', path]).decode().split(',')
        _probe[path] = (int(o[0]), int(o[1]))
    return _probe[path]

class Decoder:
    """Streams one slot's frames: 9:16 window (+pan range) of the source, graded, at WORK_H height."""
    def __init__(self, s):
        path = os.path.join(A.src, s['src'] + '.mp4'); sw, sh = probe(path)
        n = s['f1'] - s['f0']; speed = s.get('speed', 1.0)
        if sw / sh > 9 / 16: vh, vw = sh, sh * 9 / 16
        else: vw, vh = sw, sw * 16 / 9
        xc = s.get('xc', 0.5); xc0, xc1 = (xc, xc) if not isinstance(xc, tuple) else xc
        lo = min(xc0, xc1) * sw - vw / 2; hi = max(xc0, xc1) * sw + vw / 2
        if lo < 0: lo, hi = 0, max(hi, vw)
        if hi > sw: lo, hi = min(lo, sw - vw), sw
        lo, hi = max(0.0, lo), min(float(sw), hi)
        scale = WORK_H / vh
        self.ww = int(round((hi - lo) * scale / 2)) * 2
        self.cx0 = (min(max(xc0 * sw, lo + vw / 2), hi - vw / 2) - lo) * scale
        self.cx1 = (min(max(xc1 * sw, lo + vw / 2), hi - vw / 2) - lo) * scale
        g = s['g']
        vf = [f'setpts=PTS/{speed}', f'fps={FPS}',
              f'crop={int(round(hi - lo))}:{int(vh)}:{int(round(lo))}:{int((sh - vh) / 2)}',
              f'scale={self.ww}:{WORK_H}:flags=lanczos',
              f"eq=contrast={g['con']}:brightness={g['bri']}:saturation={g['sat']}:gamma={g['gam']}",
              f"vibrance=intensity={g['vib']}"]
        if scale > 1.3: vf.append('unsharp=5:5:0.7:5:5:0.0')
        cmd = ['ffmpeg', '-v', 'error', '-ss', str(s['ss']), '-i', path, '-vf', ','.join(vf),
               '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        self.n, self.fsz, self.last = n, self.ww * WORK_H * 3, None
    def next(self):
        b = self.p.stdout.read(self.fsz)
        if len(b) == self.fsz: self.last = Image.frombuffer('RGB', (self.ww, WORK_H), b, 'raw', 'RGB', 0, 1)
        return self.last      # repeat last frame if the source runs short
    def close(self):
        self.p.stdout.close(); self.p.wait()

# ---------------------------------------------------------------- graphics
def text_layer(txt, font_path, size, fill=(255, 255, 255), tracking=0, shadow=True):
    f = ImageFont.truetype(font_path, size)
    if tracking:
        widths = [f.getlength(c) for c in txt]; tw = int(sum(widths) + tracking * (len(txt) - 1))
    else:
        tw = int(f.getlength(txt))
    asc, desc = f.getmetrics(); pad = 40
    im = Image.new('RGBA', (tw + 2 * pad, asc + desc + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if tracking:
        x = pad
        for c, w_ in zip(txt, widths): d.text((x, pad), c, font=f, fill=fill); x += w_ + tracking
    else:
        d.text((pad, pad), txt, font=f, fill=fill)
    if not shadow: return im
    a = im.split()[3]
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    for blur, op, dy in ((18, 0.50, 4), (4, 0.70, 3)):
        sh = a.filter(ImageFilter.GaussianBlur(blur)).point(lambda v, op=op: int(v * op))
        layer = Image.new('RGBA', im.size, (20, 10, 10, 0)); layer.putalpha(sh)
        out.alpha_composite(layer, (0, dy) if dy >= 0 else (0, 0))
    out.alpha_composite(im)
    return out

def pin_icon(h=74, color=RED):
    S = 4; w = int(h * 0.74); im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    r = w * S / 2; cx = r; cy = r
    d.ellipse([0, 0, 2 * r, 2 * r], fill=color)
    d.polygon([(cx - r * 0.82, cy + r * 0.55), (cx + r * 0.82, cy + r * 0.55), (cx, h * S)], fill=color)
    d.ellipse([cx - r * 0.38, cy - r * 0.38, cx + r * 0.38, cy + r * 0.38], fill=(255, 255, 255))
    im = im.resize((w, h), Image.LANCZOS)
    pad = 20; out = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('RGBA', out.size, (20, 10, 10, 0)); a = Image.new('L', out.size, 0); a.paste(im.split()[3], (pad, pad + 3))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * 0.45)))
    out.alpha_composite(sh); out.alpha_composite(im, (pad, pad)); return out

def pill(txt, font_path, size, fg, bg, padx, pady):
    f = ImageFont.truetype(font_path, size); tw = f.getlength(txt); asc, desc = f.getmetrics()
    bb = f.getbbox(txt); th = bb[3] - bb[1]
    pw, ph = int(tw + 2 * padx), int(th + 2 * pady); m = 30
    im = Image.new('RGBA', (pw + 2 * m, ph + 2 * m), (0, 0, 0, 0))
    a = Image.new('L', im.size, 0); ImageDraw.Draw(a).rounded_rectangle([m, m + 8, m + pw, m + ph + 8], ph // 2, fill=95)
    sh = Image.new('RGBA', im.size, (20, 10, 10, 0)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(14))); im.alpha_composite(sh)
    d = ImageDraw.Draw(im); d.rounded_rectangle([m, m, m + pw, m + ph], ph // 2, fill=bg + (255,))
    d.text((m + padx, m + pady - bb[1]), txt, font=f, fill=fg)
    return im

class El:
    """An animated overlay element. pos = centre (x, y) in px. anim: 'rise' | 'pop' | 'drop'."""
    def __init__(self, img, pos, t_in, t_out=None, anim='rise', d_in=0.38, rise=46, scale_from=1.0):
        self.img, self.pos, self.t_in, self.t_out, self.anim = img, pos, t_in, t_out, anim
        self.d_in, self.rise, self.scale_from = d_in, rise, scale_from
    def state(self, t):
        if t < self.t_in: return None
        x = (t - self.t_in) / self.d_in; a, dy, sc = ease_out(x * 1.6), 0.0, 1.0
        self.dx = -(1 - ease_out(x)) * 120 if self.anim == 'fly' else 0.0
        if self.anim == 'rise': dy = (1 - ease_out(x)) * self.rise; sc = lerp(self.scale_from, 1.0, ease_out(x))
        elif self.anim == 'pop': sc = lerp(self.scale_from, 1.0, ease_back(x)); a = ease_out(x * 2)
        elif self.anim == 'fly':
            e = ease_out(x); dy = (1 - e) * 70; a = ease_out(x * 2.5); sc = 1.0
        elif self.anim == 'drop':
            y = min(x, 1); b = abs(math.cos(y * math.pi * 1.5)) * (1 - y) ** 2   # bounce
            dy = -90 * b if y < 1 else 0; a = ease_out(x * 3)
        if self.t_out is not None and t > self.t_out:
            y = (t - self.t_out) / 0.22
            if y >= 1: return None
            a *= 1 - ease_inout(y); dy -= 26 * ease_inout(y)
        return a, dy, sc
    def draw(self, canvas, t):
        st = self.state(t)
        if not st: return
        a, dy, sc = st; im = self.img
        if abs(sc - 1) > 1e-3:
            im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
        if a < 0.999: im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * a)))
        paste(canvas, im, int(round(self.pos[0] - im.width / 2 + getattr(self, 'dx', 0.0))), int(round(self.pos[1] - im.height / 2 + dy)))

def paste(canvas, im, x, y):
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(W, x + im.width), min(H, y + im.height)
    if x1 <= x0 or y1 <= y0: return
    canvas.alpha_composite(im, (x0, y0), (x0 - x, y0 - y, x1 - x, y1 - y))

ELS = []

def icon_layer(kind, h=78, color=RED):
    S = 4; N = h * S; im = Image.new('RGBA', (N, N), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    U = lambda pts: [(x * N, y * N) for x, y in pts]
    if kind == 'plane':
        d.rounded_rectangle([0.44 * N, 0.03 * N, 0.56 * N, 0.97 * N], radius=0.06 * N, fill=color)
        d.polygon(U([(0.5, 0.30), (0.98, 0.58), (0.98, 0.67), (0.5, 0.54), (0.02, 0.67), (0.02, 0.58)]), fill=color)
        d.polygon(U([(0.5, 0.78), (0.74, 0.91), (0.74, 0.98), (0.5, 0.92), (0.26, 0.98), (0.26, 0.91)]), fill=color)
        im = im.rotate(-45, resample=Image.BICUBIC)
    elif kind == 'sun':
        c = N / 2; d.ellipse([c - 0.24 * N, c - 0.24 * N, c + 0.24 * N, c + 0.24 * N], fill=color)
        for k in range(8):
            a = k * math.pi / 4; ca, sa = math.cos(a), math.sin(a); r0, r1, hw = 0.33 * N, 0.48 * N, 0.045 * N
            d.polygon([(c + ca * r0 - sa * hw, c + sa * r0 + ca * hw), (c + ca * r1 - sa * hw, c + sa * r1 + ca * hw),
                       (c + ca * r1 + sa * hw, c + sa * r1 - ca * hw), (c + ca * r0 + sa * hw, c + sa * r0 - ca * hw)], fill=color)
    elif kind == 'spark':
        def star(cx, cy, R, r):
            pts = []
            for k in range(8):
                a = k * math.pi / 4 - math.pi / 2; rr = R if k % 2 == 0 else r
                pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
            d.polygon(pts, fill=color)
        star(0.42 * N, 0.56 * N, 0.42 * N, 0.11 * N); star(0.80 * N, 0.18 * N, 0.17 * N, 0.05 * N)
    else:  # pin
        w = int(N * 0.74); r = w / 2; cx = N / 2; cy = r
        d.ellipse([cx - r, 0, cx + r, 2 * r], fill=color)
        d.polygon([(cx - r * 0.82, cy + r * 0.55), (cx + r * 0.82, cy + r * 0.55), (cx, N)], fill=color)
        d.ellipse([cx - r * 0.38, cy - r * 0.38, cx + r * 0.38, cy + r * 0.38], fill=(255, 255, 255))
    im = im.resize((h, h), Image.LANCZOS)
    pad = 20; out = Image.new('RGBA', (h + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('RGBA', out.size, (20, 10, 10, 0)); a = Image.new('L', out.size, 0); a.paste(im.split()[3], (pad, pad + 3))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * 0.45)))
    out.alpha_composite(sh); out.alpha_composite(im, (pad, pad)); return out

PRICE, OLD_PRICE = 3534000, 3720000   # цена по акции и обычная, в вонах
def draw_won(d, x, y, f, fill):
    """Advaken has no won sign: draw W and strike it with two bars."""
    d.text((x, y), 'W', font=f, fill=fill)
    l, t, r, b = d.textbbox((x, y), 'W', font=f); gh = b - t; th = max(2, int(gh * 0.10))
    for fy in (0.40, 0.62):
        yc = t + gh * fy; d.rectangle([l - gh * 0.06, yc - th / 2, r + gh * 0.06, yc + th / 2], fill=fill)
    return f.getlength('W')
def price_pill(value, size=92, padx=50, pady=30, final=PRICE):
    f = ImageFont.truetype(F_HEAD, size)
    fmt = lambda v: f"{v:,}".replace(',', ' ') + ' '
    tw_full = f.getlength(fmt(final)) + f.getlength('W')
    bb = f.getbbox('0W'); th = bb[3] - bb[1]
    pw, ph = int(tw_full + 2 * padx), int(th + 2 * pady); m = 30
    im = Image.new('RGBA', (pw + 2 * m, ph + 2 * m), (0, 0, 0, 0))
    a = Image.new('L', im.size, 0); ImageDraw.Draw(a).rounded_rectangle([m, m + 8, m + pw, m + ph + 8], ph // 2, fill=95)
    sh = Image.new('RGBA', im.size, (20, 10, 10, 0)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(14))); im.alpha_composite(sh)
    d = ImageDraw.Draw(im); d.rounded_rectangle([m, m, m + pw, m + ph], ph // 2, fill=NAVY + (255,))
    txt = fmt(value); tw = f.getlength(txt) + f.getlength('W'); x = m + (pw - tw) / 2; y = m + pady - bb[1]
    d.text((x, y), txt, font=f, fill=CREAM); draw_won(d, x + f.getlength(txt), y, f, CREAM)
    return im

class CountUp:
    """Price pill that pops in and counts up to the final value."""
    def __init__(self, pos, t_in, t_out=None, dur=0.9):
        self.pos, self.t_in, self.t_out, self.dur = pos, t_in, t_out, dur; self.final = price_pill(PRICE); self.cache = {}
    def draw(self, canvas, t):
        if t < self.t_in: return
        x = (t - self.t_in) / self.dur
        if x >= 1: im = self.final
        else:
            v = int(round(PRICE * ease_out(x) / 10000)) * 10000
            im = self.cache.get(v) or self.cache.setdefault(v, price_pill(v))
        sx = (t - self.t_in) / 0.42; sc = lerp(0.7, 1.0, ease_back(sx)); a = ease_out(sx * 2)
        if self.t_out is not None and t > self.t_out:
            y = (t - self.t_out) / 0.22
            if y >= 1: return
            a *= 1 - ease_inout(y)
        if abs(sc - 1) > 1e-3: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
        if a < 0.999: im = im.copy(); im.putalpha(im.split()[3].point(lambda v, a=a: int(v * a)))
        paste(canvas, im, int(round(self.pos[0] - im.width / 2)), int(round(self.pos[1] - im.height / 2)))

def fit(txt, fp, size, maxw=960):
    while ImageFont.truetype(fp, size).getlength(txt) > maxw: size -= 2
    return size

def title_block():
    t0, t_out = 0.12, beat(10) - 0.22
    ELS.append(El(text_layer('23.12.2026 – 03.01.2027 · 11 ДНЕЙ', F_BODY, 40, tracking=4), (W / 2, 318), t0, t_out))
    f = ImageFont.truetype(F_HEAD, 170); word = 'БАЛИ'; total = f.getlength(word); x = W / 2 - total / 2
    for i, c in enumerate(word):
        cw = f.getlength(word[:i + 1]) - f.getlength(word[:i])
        ELS.append(El(text_layer(c, F_HEAD, 170), (x + cw / 2, 450), t0 + 0.10 + i * 0.06, t_out, rise=70, scale_from=1.35))
        x += cw
    s2 = fit('РОЖДЕСТВО И НОВЫЙ ГОД', F_HEAD, 56)
    words = ['РОЖДЕСТВО', 'И', 'НОВЫЙ', 'ГОД']; f2 = ImageFont.truetype(F_HEAD, s2); sp = f2.getlength(' ')
    tot = sum(f2.getlength(w_) for w_ in words) + sp * (len(words) - 1); x = W / 2 - tot / 2
    for i, w_ in enumerate(words):
        ww = f2.getlength(w_); ELS.append(El(text_layer(w_, F_HEAD, s2), (x + ww / 2, 592), t0 + 0.50 + i * 0.10, t_out)); x += ww + sp
    ELS.append(El(pill('два праздника в одном путешествии', F_BODY, 36, NAVY, CREAM, 34, 17), (W / 2, 690), t0 + 0.95, t_out))

def label(small, big, icon, k_in, k_out):
    t_in, t_out = beat(k_in) + 0.06, beat(k_out) - 0.16
    ELS.append(El(text_layer(small, F_BODY, fit(small, F_BODY, 40)), (W / 2, 392), t_in, t_out, rise=36))
    big_l = text_layer(big, F_HEAD, fit(big, F_HEAD, 66, 860)); ic = icon_layer(icon, 62 if icon != 'pin' else 60)
    gap = -26; tot = ic.width + gap + big_l.width; x0 = W / 2 - tot / 2
    anim = {'pin': 'drop', 'plane': 'fly'}.get(icon, 'pop')
    ELS.append(El(ic, (x0 + ic.width / 2, 494), t_in + 0.14, t_out, anim=anim, d_in=0.5, scale_from=0.3))
    ELS.append(El(big_l, (x0 + ic.width + gap + big_l.width / 2, 498), t_in + 0.10, t_out, rise=40))

def holidays(k_in, k_out):
    t_in, t_out = beat(k_in) + 0.06, beat(k_out) - 0.16
    ELS.append(El(pill('25.12 · РОЖДЕСТВО ПОД ПАЛЬМАМИ', F_HEAD, fit('25.12 · РОЖДЕСТВО ПОД ПАЛЬМАМИ', F_HEAD, 46, 860), NAVY, ORANGE, 40, 22), (W / 2, 400), t_in + 0.05, t_out, anim='pop', d_in=0.42, scale_from=0.6))
    ELS.append(El(pill('31.12 · НОВЫЙ ГОД ВМЕСТЕ', F_HEAD, fit('25.12 · РОЖДЕСТВО ПОД ПАЛЬМАМИ', F_HEAD, 46, 860), NAVY, CREAM, 40, 22), (W / 2, 520), beat(47) + 0.08, t_out, anim='pop', d_in=0.42, scale_from=0.6))
    ELS.append(El(text_layer('праздничный стол от JEJU TRIP для всей группы', F_BODY, 38), (W / 2, 630), beat(47) + 0.35, t_out, rise=30))

K_LOGO = 59
def finale():
    t_in, t_out = beat(50) + 0.10, beat(K_LOGO) - 0.16
    ELS.append(El(text_layer('11 дней / 10 ночей · мини-группа 10 человек', F_BODY, fit('11 дней / 10 ночей · мини-группа 10 человек', F_BODY, 40)), (W / 2, 330), t_in, t_out, rise=36))
    ELS.append(El(pill('ВСЕГО 10 МЕСТ', F_HEAD, 72, CREAM, NAVY, 54, 30), (W / 2, 440), t_in + 0.16, t_out, anim='pop', d_in=0.42, scale_from=0.6))
    ELS.append(El(pill('АВИАБИЛЕТЫ ВКЛЮЧЕНЫ', F_HEAD, 44, NAVY, ORANGE, 40, 22), (W / 2, 560), t_in + 1.0, t_out, anim='pop', d_in=0.42, scale_from=0.6))
    ELS.append(El(text_layer('вылет из Инчхона · авторский тур JEJU TRIP', F_BODY, 34), (W / 2, 648), t_in + 1.2, t_out, rise=24))
    ELS.append(El(pill('ПИШИТЕ БАЛИ В DIRECT', F_HEAD, 54, NAVY, ORANGE, 46, 26), (W / 2, 1450), beat(54) + 0.10, t_out, anim='pop', d_in=0.42, scale_from=0.6))
    ELS.append(El(pill('пришлём программу и условия бронирования', F_BODY, 34, NAVY, CREAM, 34, 17), (W / 2, 1570), beat(54) + 0.35, t_out, rise=30))
    t_h = beat(K_LOGO) + 0.02
    logo = Image.open(os.path.join(HERE, 'logo.png')).convert('RGBA'); lh = 205
    logo = logo.resize((int(logo.width * lh / logo.height), lh), Image.LANCZOS)
    fj = ImageFont.truetype(F_HEAD, 58); sp = fj.getlength(' ')
    wj, wt = fj.getlength('JEJU'), fj.getlength('TRIP'); tw = wj + sp + wt
    cw, ch = int(max(logo.width, tw) + 110), lh + 150; pad = 50
    card = Image.new('RGBA', (cw + 2 * pad, ch + 2 * pad), (0, 0, 0, 0))
    m = Image.new('L', card.size, 0); ImageDraw.Draw(m).rounded_rectangle([pad, pad + 10, pad + cw, pad + ch + 10], 52, fill=110)
    shl = Image.new('RGBA', card.size, (40, 20, 10, 0)); shl.putalpha(m.filter(ImageFilter.GaussianBlur(22))); card.alpha_composite(shl)
    d = ImageDraw.Draw(card); d.rounded_rectangle([pad, pad, pad + cw, pad + ch], 52, fill=(251, 246, 236, 245))
    card.alpha_composite(logo, (pad + (cw - logo.width) // 2, pad + 30))
    x = pad + (cw - tw) / 2; y = pad + 30 + lh + 12
    d.text((x, y), 'JEJU', font=fj, fill=RED); d.text((x + wj + sp, y), 'TRIP', font=fj, fill=ORANGE)
    ELS.append(El(card, (W / 2, 1060), t_h, None, anim='pop', d_in=0.45, scale_from=0.5))
    ELS.append(El(pill('директор Елена Шин приглашает вас', F_BODY, 34, NAVY, CREAM, 34, 17), (W / 2, 1320), t_h + 0.35, None, rise=30))

title_block()
label('джунгли · водопады · рисовые террасы · Лес обезьян', 'УБУД', 'pin', 10, 18)
label('джип-сафари и виды над облаками', 'РАССВЕТ НА ВУЛКАНЕ', 'sun', 18, 24)
label('два дня · приватная лодка · снорклинг с мантами', 'НУСА-ПЕНИДА', 'pin', 24, 32)
label('королевский SPA · церемония очищения', 'БАЛИЙСКИЕ ТРАДИЦИИ', 'spark', 32, 38)
label('серфинг · пляжные клубы · закаты', 'ПРИКЛЮЧЕНИЯ', 'sun', 38, 44)
holidays(44, 50)
finale()
PETALS = []

# light leak image (screen-blended, only brightens)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
def leak_frame(cx, cy, rad, color):
    g = np.exp(-(((xx - cx) / rad) ** 2 + ((yy - cy) / (rad * 1.6)) ** 2))
    return g[..., None] * np.array(color, np.float32)[None, None, :] / 255.0

TOPSHADE = (0.42 * np.clip(1 - np.arange(H, dtype=np.float32) / 860, 0, 1) ** 1.6)[:, None, None]
def effects(arr, t):
    out = arr
    if t < beat(K_LOGO): out = out * (1 - TOPSHADE) + np.array(NAVY, np.float32) * 0.5 * TOPSHADE
    for t0, peak, dur in FLASH:
        if t0 - 0.034 <= t < t0 + dur:
            a = peak * (1 - ease_out((t - t0) / dur)) if t >= t0 else peak * 0.5
            out = out + (255 - out) * a
    for t0, peak in LEAKS:
        d = 0.42
        if t0 - 0.10 <= t < t0 + d:
            x = (t - t0 + 0.10) / (d + 0.10); a = peak * math.sin(math.pi * x)
            L = leak_frame(lerp(-200, W + 300, x), H * 0.35, 520, (255, 196, 160)) * a
            out = 255 - (255 - out) * (1 - L)
    return out

# ---------------------------------------------------------------- main loop
f_from = int(A.t_from * FPS); f_to = NFR if A.t_to is None else min(NFR, int(A.t_to * FPS))
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-ss', f'{f_from / FPS:.4f}', '-i', A.music, '-map', '0:v', '-map', '1:a',
                        '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-profile:v', 'high',
                        '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
                        '-af', f'afade=t=out:st={max(0, (f_to - f_from) / FPS - 0.25):.3f}:d=0.25',
                        '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', A.out], stdin=subprocess.PIPE)
if A.stills: os.makedirs(A.stills, exist_ok=True)

for si, s in enumerate(SLOTS):
    if s['f1'] <= f_from or s['f0'] >= f_to: continue
    dec = Decoder(s); n = s['f1'] - s['f0']
    for i in range(n):
        f = s['f0'] + i; src = dec.next()
        if f < f_from or f >= f_to: continue
        t = f / FPS; lt = i / FPS; x = i / max(1, n - 1)
        z = lerp(s['z'][0], s['z'][1], ease_inout(x))
        pk = s.get('punch', 0)
        if pk: z *= 1 + pk * (1 - ease_out(lt / 0.30))
        cx = lerp(dec.cx0, dec.cx1, ease_inout(x)); vw, vh = WORK_W / z, WORK_H / z
        cx = min(max(cx, vw / 2), dec.ww - vw / 2); cy = min(max(WORK_H / 2, vh / 2), WORK_H - vh / 2)
        frame = src.resize((W, H), Image.BICUBIC, box=(cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2))
        arr = np.asarray(frame, dtype=np.float32)
        arr = effects(arr, t)
        canvas = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
        for pt in PETALS: pt.draw(canvas, t)
        for e in ELS: e.draw(canvas, t)
        out = canvas.convert('RGB')
        enc.stdin.write(out.tobytes())
        if A.stills and f % A.stills_every == 0: out.save(os.path.join(A.stills, f'f{f:04d}.jpg'), quality=85)
    dec.close()
    print(f'slot {si:2d} {s["src"]:<22} frames {s["f0"]}-{s["f1"]}', flush=True)
enc.stdin.close(); enc.wait()
print('done', A.out)

