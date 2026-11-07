# Склейки (ffmpeg scdet) и выравнивание баланса белого между сценами по светлым стенам.
import subprocess, numpy as np

CUTS = [0, 1.567, 4.767, 5.7, 6.433, 8.9, 12.6, 13.867, 15.633, 17.733, 23.167, 32.9, 34.8]
TARGET = np.array([232, 226, 217], np.float32)  # тёплый молочный цвет стен


def frame(src, t, w=270):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', src, '-frames:v', '1', '-vf', f'scale={w}:-2',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, w, 3)


def shot_gains(src, dur):
    ends = CUTS[1:] + [dur]
    gains = []
    for a, b in zip(CUTS, ends):
        px = []
        for t in np.linspace(a + 0.1, b - 0.1, 3):
            f = frame(src, t).reshape(-1, 3).astype(np.float32)
            y = f.mean(1); sat = f.max(1) - f.min(1)
            sel = f[(y > np.percentile(y, 60)) & (sat < 40) & (y < 250)]
            if len(sel): px.append(sel)
        m = np.concatenate(px).mean(0)
        # выравниваем только оттенок (соотношение каналов), яркость почти не трогаем
        g = (TARGET / TARGET.mean()) / (m / m.mean())
        g = 1 + (g - 1) * 0.6
        g *= np.clip(TARGET.mean() / m.mean(), 0.98, 1.03)
        gains.append(np.clip(g, 0.93, 1.07))
    return gains


def gains_at(gains, t):
    i = max(k for k, c in enumerate(CUTS) if c <= t + 1e-6)
    return gains[i]
