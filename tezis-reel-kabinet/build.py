# Сборка Reels: python3 build.py <папка с IMG_xxxx.MOV>  ->  tezis_reel_kabinet.mp4
# Нужны ffmpeg, Node.js + Playwright, numpy. Цвет кадров не меняется (кроме ч/б финала по сценарию).
import json, os, subprocess, sys
import numpy as np
from timeline import SEGMENTS, HOOK, OUTRO

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1]
WORK = os.path.join(HERE, 'work'); os.makedirs(WORK, exist_ok=True)
FPS, SR = 30, 48000
src = lambda n: os.path.join(SRC, f'{n}.MOV')
run = lambda cmd: subprocess.run(cmd, check=True)
fr = lambda t: round(t * FPS) / FPS  # всё по кадрам

# --- 1. таймлайн ролика
t = 0.0; caps = []; pieces = []; seg_t = []
TAIL = 1.6  # стоп-кадр в конце: пустой дверной проём
for i, s in enumerate(SEGMENTS):
    a0, a1 = s['a'][1], s['a'][2]
    dur = fr(a1 - a0)
    seg_t.append((t, t + dur))
    for (n, v0, v1) in s['v']:
        pieces.append(dict(n=n, ss=v0, d=fr(v1 - v0), bw=s.get('bw', False)))
    for (c0, c1, txt) in s['cap']:
        caps.append((fr(t + c0 - a0), fr(t + c1 - a0), txt))
    t += dur
TOTAL = fr(t + TAIL)
assert abs(sum(p['d'] for p in pieces) - (TOTAL - TAIL)) < 0.2, 'видео и звук разной длины'
rec0, rec1 = seg_t[-1][0], TOTAL
outro0 = caps[-1][1] + 0.1

# --- 2. оверлеи PNG (Playwright, прозрачный фон)
ov = [dict(f='hook.png', a=0.25, b=3.1, show={'hook': HOOK})]
for k, (a, b, txt) in enumerate(caps):
    ov.append(dict(f=f'cap_{k:02d}.png', a=a, b=b, show={'cap': txt}))
ov.append(dict(f='outro.png', a=outro0, b=TOTAL, show={'outro': OUTRO}))
json.dump([dict(f=os.path.join(WORK, o['f']), show=o['show']) for o in ov] +
          [dict(f=os.path.join(WORK, 'grad.png'), show={'grad': 1}), dict(f=os.path.join(WORK, 'rec.png'), show={'rec': 1}), dict(f=os.path.join(WORK, 'recoff.png'), show={'recoff': 1})],
          open(os.path.join(WORK, 'ov.json'), 'w'), ensure_ascii=False)
run(['node', os.path.join(HERE, 'render_overlay.js'), os.path.join(WORK, 'ov.json')])

# --- 3. видео-куски: 4K -> 1080x1920, без цветокоррекции
lst = []
for k, p in enumerate(pieces):
    out = os.path.join(WORK, f'p{k:02d}.mp4'); lst.append(out)
    vf = 'scale=1080:1920:flags=lanczos,fps=30,format=yuv420p' + (',hue=s=0' if p['bw'] else '')
    if k == len(pieces) - 1: vf += f',tpad=stop_mode=clone:stop_duration={TAIL}'
    run(['ffmpeg', '-v', 'error', '-y', '-ss', str(p['ss']), '-i', src(p['n']), '-t', str(p['d']), '-an',
         '-vf', vf, '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', out])
with open(os.path.join(WORK, 'list.txt'), 'w') as f:
    f.writelines(f"file '{x}'\n" for x in lst)
base = os.path.join(WORK, 'base.mp4')
run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(WORK, 'list.txt'), '-c', 'copy', base])

# --- 4. звук: дубли диалога + тихий напряжённый фон + вибрация телефона
def load(n, a0, a1):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(a0), '-i', src(n), '-t', str(fr(a1 - a0)), '-vn', '-ac', '1', '-ar', str(SR),
                          '-af', 'highpass=f=90,afftdn=nf=-30', '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).copy()
    n_ = int(round(fr(a1 - a0) * SR)); x = np.pad(x, (0, max(0, n_ - len(x))))[:n_]
    f = int(0.012 * SR); ramp = np.linspace(0, 1, f); x[:f] *= ramp; x[-f:] *= ramp[::-1]
    # выравниваем громкость дублей по речи
    fr_ = x[: len(x) // 480 * 480].reshape(-1, 480); e = np.sqrt((fr_ ** 2).mean(1))
    sp = e[e > np.percentile(e, 70)]
    return x * (0.08 / max(sp.mean(), 1e-5))
dlg = np.concatenate([load(*s['a']) for s in SEGMENTS] + [np.zeros(int(TAIL * SR), np.float32)])
N = len(dlg); tt = np.arange(N) / SR
rng = np.random.default_rng(7)
# фон: низкий гул + тихий «пульс», уходит на словах «в гардеробную»
reveal = caps[[i for i, c in enumerate(caps) if 'гардеробную' in c[2]][0]][0] + 1.2
env = np.clip(tt / 1.5, 0, 1) * np.clip((reveal - tt) / 0.8, 0, 1)
drone = (np.sin(2 * np.pi * 55 * tt) * 0.6 + np.sin(2 * np.pi * 82.4 * tt + 1) * 0.3 + np.sin(2 * np.pi * 110.2 * tt) * 0.12)
drone *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.25 * tt)
noise = np.convolve(rng.standard_normal(N), np.ones(400) / 400, 'same') * 3
pulse = np.zeros(N)
for b in np.arange(1.0, reveal, 0.82):  # мягкий удар раз в такт
    i = int(b * SR); L = int(0.35 * SR)
    if i + L < N: pulse[i:i + L] += np.sin(2 * np.pi * 48 * tt[:L]) * np.exp(-tt[:L] * 14)
bed = (drone * 0.022 + noise * 0.012 + pulse * 0.05) * env
# вибрация телефона в начале ч/б сцены (до «Да, дорогой»)
sfx = np.zeros(N)
for b in (rec0 + 0.15, rec0 + 0.75):
    i = int(b * SR); L = int(0.4 * SR)
    sfx[i:i + L] += np.sign(np.sin(2 * np.pi * 150 * tt[:L])) * 0.035 * np.sin(np.pi * tt[:L] / 0.4)
# короткий сигнал «запись» на склейке в ч/б
i = int(rec0 * SR); L = int(0.09 * SR); sfx[i:i + L] += np.sin(2 * np.pi * 1760 * tt[:L]) * 0.06 * np.hanning(L)
mix = (dlg + bed + sfx).astype(np.float32)
wav = os.path.join(WORK, 'mix.f32')
mix.tofile(wav)
audio = os.path.join(WORK, 'audio.wav')
# громкость в два прохода: замер, затем точная нормализация до -14 LUFS
m = subprocess.run(['ffmpeg', '-hide_banner', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', wav, '-af',
                    'loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
m = json.loads(m[m.rindex('{'):])
ln = (f"loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
      f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', wav,
     '-af', ln + ',volume=1.3dB,alimiter=limit=0.89:level=false', '-ar', str(SR), '-ac', '2', audio])

# --- 5. наложение надписей и REC
inp = ['-i', base, '-i', audio]; fc = []; last = '0:v'; k = 2
def add(png, a, b, enable=None, fade=True):
    global last, k
    inp.extend(['-loop', '1', '-t', str(TOTAL), '-i', os.path.join(WORK, png)])
    f = f'[{k}:v]format=rgba'
    if fade: f += f',fade=t=in:st={a}:d=0.18:alpha=1,fade=t=out:st={max(a, b - 0.14):.3f}:d=0.14:alpha=1'
    fc.append(f + f'[o{k}]')
    fc.append(f"[{last}][o{k}]overlay=0:0:enable='{enable or f'between(t,{a},{b})'}'[v{k}]")
    last = f'v{k}'; k += 1
add('grad.png', 0, TOTAL, fade=False)
for o in ov: add(o['f'], round(o['a'], 3), round(o['b'], 3))
add('rec.png', rec0, rec1, enable=f"between(t,{rec0},{rec1})*lt(mod(t-{rec0},1),0.55)", fade=False)
add('recoff.png', rec0, rec1, enable=f"between(t,{rec0},{rec1})*gte(mod(t-{rec0},1),0.55)", fade=False)
font = os.path.join(HERE, 'fonts', 'Onest-600.ttf')
fc.append(f"[{last}]drawtext=fontfile={font}:timecode='23\\:47\\:12\\:00':rate=30:fontsize=30:fontcolor=white:"
          f"x=w-64-tw:y=262:shadowcolor=black@0.4:shadowx=0:shadowy=1:enable='between(t,{rec0},{rec1})'[vout]")
out = os.path.join(HERE, 'tezis_reel_kabinet.mp4')
run(['ffmpeg', '-v', 'error', '-y', *inp, '-filter_complex', ';'.join(fc), '-map', '[vout]', '-map', '1:a',
     '-c:v', 'libx264', '-crf', '17', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k',
     '-t', str(TOTAL), '-movflags', '+faststart', out])
json.dump(dict(total=TOTAL, caps=caps, seg=seg_t), open(os.path.join(WORK, 'timeline.json'), 'w'), ensure_ascii=False, indent=1)
print('ok', out, TOTAL)
