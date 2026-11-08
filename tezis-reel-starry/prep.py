# Готовит кадры для ролика: увеличение до 1080x1920 и вечерний свет (кодом, без генерации).
# python3 prep.py <папка с before/empty_before/empty_blue/after.png> <папка вывода img/>
import sys, os
import numpy as np, cv2
src, out = sys.argv[1:3]
os.makedirs(out, exist_ok=True)
W, H = 1080, 1920

def up(name):
    im = cv2.imread(os.path.join(src, name + '.png'))
    im = cv2.resize(im, (W, H), interpolation=cv2.INTER_LANCZOS4)
    blur = cv2.GaussianBlur(im, (0, 0), 1.2)
    return cv2.addWeighted(im, 1.35, blur, -0.35, 0)  # лёгкая резкость после увеличения

for n, o in [('shell', 'shell'), ('empty_blue', 'empty_blue'), ('after', 'after')]:
    cv2.imwrite(os.path.join(out, o + '.jpg'), up(n), [cv2.IMWRITE_JPEG_QUALITY, 94])

# вечер: дневной свет приглушён и холоднее, у светильников тёплое свечение
a = up('after').astype(np.float32) / 255
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
night = a * 0.58
night[..., 0] *= 1.12; night[..., 2] *= 0.85  # BGR: холоднее
glow = np.zeros_like(a)
import json
lamps = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lamps.json')))  # шары-светильники
for x, y, r, k in lamps:
    d = np.sqrt((xx - x) ** 2 + (yy - y) ** 2)
    g = np.exp(-(d / r) ** 2 * 2.2) * k
    glow += g[..., None] * np.array([0.55, 0.78, 1.0])  # тёплый (BGR)
    core = np.exp(-(d / 46) ** 2)
    night = night * (1 - core[..., None]) + a * core[..., None] * 1.25
lit = night + glow * a * 1.0 + glow * 0.06 + a * 0.16 * np.array([0.75, 0.92, 1.08])  # общий тёплый свет по комнате
# окно - вечерняя синева
win = np.zeros((H, W), np.float32); cv2.rectangle(win, (115, 760), (560, 1240), 1, -1)
win = cv2.GaussianBlur(win, (0, 0), 12)[..., None]
lit = lit * (1 - win * 0.78) + win * 0.78 * (a * 0.22 * np.array([1.7, 1.0, 0.55]))
cv2.imwrite(os.path.join(out, 'night.jpg'), np.clip(lit * 255, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 94])
print('ok')
