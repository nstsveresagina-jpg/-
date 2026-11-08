# Эскизы пар «2026 / 2027» кодом: правильная геометрия деталей, потом нейросеть делает фотореализм (img2img).
# python3 sketch.py <папка вывода>
import os, sys
import numpy as np, cv2

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
W, H = 832, 1216
rng = np.random.default_rng(5)


def noise(h, w, scales=((4, .5), (16, .3), (64, .2)), seed=0):
    r = np.random.default_rng(seed); out = np.zeros((h, w), np.float32)
    for s, a in scales:
        n = r.standard_normal((h // s + 2, w // s + 2)).astype(np.float32)
        out += cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC) * a
    return out


def plaster(color, seed=1, amp=9, h=H, w=W):
    n = noise(h, w, seed=seed)
    img = np.ones((h, w, 3), np.float32) * np.array(color[::-1], np.float32)  # RGB -> BGR
    return img + n[..., None] * amp


def light(img, cx=.2, cy=.1, k=.18):
    h, w = img.shape[:2]; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx / w - cx) ** 2) + ((yy / h - cy) ** 2))
    return img * (1 + k * (0.6 - d))[..., None]


def shadow(img, mask, dx, dy, blur, a):
    m = cv2.GaussianBlur(np.roll(np.roll(mask, dy, 0), dx, 1), (0, 0), blur)
    return img * (1 - a * m[..., None])


def fill(img, mask, color, a=1.0):
    c = np.array(color[::-1], np.float32)
    return img * (1 - a * mask[..., None]) + c * a * mask[..., None]


def rect_mask(x0, y0, x1, y1, r=0, h=H, w=W):
    m = np.zeros((h, w), np.float32)
    if r: cv2.rectangle(m, (x0 + r, y0), (x1 - r, y1), 1, -1); cv2.rectangle(m, (x0, y0 + r), (x1, y1 - r), 1, -1); [cv2.circle(m, p, r, 1, -1) for p in [(x0 + r, y0 + r), (x1 - r, y0 + r), (x0 + r, y1 - r), (x1 - r, y1 - r)]]
    else: cv2.rectangle(m, (x0, y0), (x1, y1), 1, -1)
    return m


def circ(cx, cy, r, h=H, w=W):
    m = np.zeros((h, w), np.float32); cv2.circle(m, (cx, cy), r, 1, -1, cv2.LINE_AA); return m


def line(img, p0, p1, color, th, a=1.0):
    m = np.zeros(img.shape[:2], np.float32); cv2.line(m, p0, p1, 1, th, cv2.LINE_AA); return fill(img, m, color, a)


def save(name, img):
    cv2.imwrite(os.path.join(OUT, name + '.png'), np.clip(img, 0, 255).astype(np.uint8))


def socket_insert(img, cx, cy, base):
    """круглое гнездо евророзетки с отверстиями и заземлением"""
    rec = circ(cx, cy, 112)
    img = fill(img, rec, tuple(int(c * .93) for c in base))
    inner = cv2.GaussianBlur(circ(cx - 6, cy - 8, 104), (0, 0), 7) - cv2.GaussianBlur(circ(cx, cy, 104), (0, 0), 7)
    img = img * (1 - 0.35 * np.clip(inner, 0, 1)[..., None])
    for dx in (-46, 46): img = fill(img, circ(cx + dx, cy, 15), (25, 22, 20))
    img = fill(img, circ(cx, cy, 9), (150, 150, 150))
    for dy in (-96, 96): img = fill(img, rect_mask(cx - 16, cy + dy - 10, cx + 16, cy + dy + 10), (190, 180, 160))
    return img


def make_socket():
    wall = light(plaster((205, 192, 176), 1, 10))
    cx, cy = 416, 600
    # 2026: белая рамка на стене
    a = wall.copy(); fr = rect_mask(cx - 200, cy - 200, cx + 200, cy + 200, 18)
    a = shadow(a, fr, 14, 18, 16, .35)
    a = fill(a, fr, (238, 236, 231)); a = light(a, .3, .2, .08) * (1 - 0) + 0
    a = line(a, (cx - 196, cy - 197), (cx + 196, cy - 197), (255, 255, 255), 3, .7)
    plate = rect_mask(cx - 150, cy - 150, cx + 150, cy + 150, 6)
    a = fill(a, plate, (232, 230, 224)); a = line(a, (cx - 150, cy + 150), (cx + 150, cy + 150), (200, 198, 192), 2, .8)
    a = socket_insert(a, cx, cy, (232, 230, 224))
    save('socket_2026', a)
    # 2027: розетка в цвет стены, вровень, тонкий шов вокруг
    b = wall.copy()
    for x0, y0, x1, y1 in [(cx - 170, cy - 170, cx + 170, cy + 170)]:
        m = np.zeros((H, W), np.float32); cv2.rectangle(m, (x0, y0), (x1, y1), 1, 3, cv2.LINE_AA)
        b = fill(b, m, (120, 110, 100), .55)
        b = line(b, (x0 + 3, y0 + 3), (x1 - 3, y0 + 3), (240, 232, 222), 2, .5)
    b = socket_insert(b, cx, cy, (203, 190, 174))
    save('socket_2027', b)


def make_skirting():
    wall = plaster((236, 232, 226), 2, 6)
    floor_y = 860
    img = wall.copy()
    # пол: доски дуба в перспективе
    fh = H - floor_y
    planks = np.zeros((600, 2400, 3), np.float32)
    for i, x in enumerate(range(0, 2400, 150)):
        tone = 200 + rng.integers(-12, 12)
        planks[:, x:x + 150] = np.array([tone * .62, tone * .8, tone])  # BGR дуб
        planks[:, x:x + 2] *= .75
    planks += noise(600, 2400, ((3, .6), (40, .4)), 7)[..., None] * 10
    src = np.float32([[0, 0], [2400, 0], [2400, 600], [0, 600]])
    dst = np.float32([[-200, floor_y], [W + 200, floor_y], [W + 1400, H + 300], [-1400, H + 300]])
    M = cv2.getPerspectiveTransform(src, dst)
    fl = cv2.warpPerspective(planks, M, (W, H))
    fm = np.zeros((H, W), np.float32); fm[floor_y:] = 1
    img = img * (1 - fm[..., None]) + fl * fm[..., None]
    img = light(img, .15, .3, .15)
    # 2026: высокий белый плинтус
    a = img.copy(); sk = rect_mask(0, floor_y - 120, W, floor_y)
    a = fill(a, sk, (244, 243, 240))
    a = line(a, (0, floor_y - 120), (W, floor_y - 120), (255, 255, 255), 4, .9)
    a = line(a, (0, floor_y - 112), (W, floor_y - 112), (190, 188, 184), 3, .6)
    sh = np.zeros((H, W), np.float32); sh[floor_y - 140:floor_y - 120] = 1
    a = a * (1 - .12 * cv2.GaussianBlur(sh, (0, 0), 6)[..., None])
    a = line(a, (0, floor_y + 2), (W, floor_y + 2), (90, 80, 70), 3, .5)
    save('skirting_2026', a)
    # 2027: теневой плинтус - тёмная щель, стена вровень
    b = img.copy(); gap = rect_mask(0, floor_y - 18, W, floor_y)
    b = fill(b, gap, (38, 34, 32))
    g2 = np.zeros((H, W), np.float32); g2[floor_y - 40:floor_y - 18] = np.linspace(0, 1, 22)[:, None]
    b = b * (1 - .18 * g2[..., None])
    b = line(b, (0, floor_y - 19), (W, floor_y - 19), (250, 248, 244), 2, .8)
    save('skirting_2027', b)


def make_vent():
    ceil = light(plaster((236, 233, 228), 3, 7), .5, .3, .2)
    # угол каменной стены снизу
    stone = plaster((222, 205, 178), 4, 14)
    yy, xx = np.mgrid[0:H, 0:W]
    sm = ((yy > 1000 + 0.18 * np.abs(xx - W / 2))).astype(np.float32)
    img = ceil * (1 - sm[..., None]) + stone * sm[..., None]
    img = line(img, (W // 2, 1000), (W // 2, H), (150, 135, 115), 2, .7)
    cx, cy = 416, 520
    a = img.copy(); sq = rect_mask(cx - 190, cy - 190, cx + 190, cy + 190, 14)
    a = shadow(a, sq, 8, 12, 14, .25); a = fill(a, sq, (240, 239, 236))
    a = fill(a, circ(cx, cy, 150), (228, 227, 223))
    for r in range(30, 150, 18):
        m = np.zeros((H, W), np.float32); cv2.circle(m, (cx, cy), r, 1, 5, cv2.LINE_AA); a = fill(a, m, (120, 118, 112), .75)
    for ang in (0, 90):
        p = (int(cx + 150 * np.cos(np.radians(ang))), int(cy + 150 * np.sin(np.radians(ang)))); q = (2 * cx - p[0], 2 * cy - p[1])
        a = line(a, p, q, (232, 231, 227), 8)
    save('vent_2026', a)
    b = img.copy(); m = np.zeros((H, W), np.float32); cv2.circle(m, (cx, cy), 170, 1, 8, cv2.LINE_AA)
    b = fill(b, m, (70, 66, 62), .8)
    b = fill(b, circ(cx + 3, cy + 4, 160) - circ(cx, cy, 160) * 0 , (236, 233, 228), 0)  # диск в цвет потолка
    save('vent_2027', b)


def tiled(color, tile, seed, w=W, h=H, grout=(170, 165, 158)):
    img = plaster(color, seed, 8, h, w)
    img += noise(h, w, ((8, .5), (90, .5)), seed + 10)[..., None] * 12
    for x in range(0, w, tile): img = line(img, (x, 0), (x, h), grout, 2, .8)
    for y in range(0, h, tile): img = line(img, (0, y), (w, y), grout, 2, .8)
    return img


def make_drain():
    # пол в перспективе из большой плитки + стены сзади
    floor = tiled((196, 192, 186), 300, 11, 1800, 1800)
    src = np.float32([[0, 0], [1800, 0], [1800, 1800], [0, 1800]])
    dst = np.float32([[-160, 380], [W + 160, 380], [W + 1100, H + 200], [-1100, H + 200]])
    M = cv2.getPerspectiveTransform(src, dst)
    fl = cv2.warpPerspective(floor, M, (W, H))
    wall = tiled((186, 182, 176), 260, 12)
    fm = np.zeros((H, W), np.float32); fm[380:] = 1
    img = light(wall * (1 - fm[..., None]) + fl * fm[..., None], .3, .2, .15)
    img = line(img, (0, 380), (W, 380), (120, 115, 108), 3, .7)
    a = img.copy()
    pts = np.float32([[0, 0], [1, 0], [1, 1], [0, 1]]) * 260 + np.float32([770, 900])
    q = cv2.perspectiveTransform(pts[None], M)[0].astype(np.int32)
    m = np.zeros((H, W), np.float32); cv2.fillPoly(m, [q], 1); a = fill(a, m, (170, 172, 175))
    for i in range(1, 7):
        for j in range(1, 7):
            p = cv2.perspectiveTransform(np.float32([[[770 + i * 37, 900 + j * 37]]]), M)[0, 0].astype(int)
            a = fill(a, circ(int(p[0]), int(p[1]), 6), (40, 40, 42))
    for c in q: a = line(a, tuple(c), tuple(cv2.perspectiveTransform(np.float32([[[0 if c[0] < W / 2 else 1800, 600 if c[1] < 900 else 1800]]]), M)[0, 0].astype(int)), (160, 155, 148), 2, .7)
    save('drain_2026', a)
    b = img.copy()
    pts = np.float32([[150, 60], [1650, 60], [1650, 140], [150, 140]])
    q = cv2.perspectiveTransform(pts[None], M)[0].astype(np.int32)
    m = np.zeros((H, W), np.float32); cv2.fillPoly(m, [q], 1); b = fill(b, m, (178, 180, 183))
    b = line(b, tuple(q[3]), tuple(q[2]), (240, 242, 245), 2, .8)
    b = line(b, (W - 120, 380), (W - 40, H), (230, 238, 236), 6, .35)  # кромка стеклянной перегородки
    save('drain_2027', b)


def make_shower():
    wall = light(tiled((196, 190, 182), 400, 21), .3, .1, .2)
    wall = fill(wall, rect_mask(700, 600, W, 820), (120, 112, 104), .55)  # ниша справа
    a = wall.copy()
    a = shadow(a, rect_mask(296, 250, 312, 860), 10, 6, 8, .25); a = fill(a, rect_mask(296, 250, 312, 860), (205, 208, 212))
    for y in (270, 840): a = fill(a, rect_mask(280, y - 10, 330, y + 10, 4), (190, 193, 197))
    a = fill(a, rect_mask(300, 470, 340, 520, 6), (195, 198, 202))
    hc = (380, 330); a = fill(a, circ(*hc, 62), (210, 212, 215)); a = fill(a, circ(*hc, 50), (150, 152, 156))
    pts = np.array([[350, 400], [330, 520], [420, 900], [440, 1120], [330, 1150], [300, 1020]], np.int32)
    m = np.zeros((H, W), np.float32); cv2.polylines(m, [pts], False, 1, 6, cv2.LINE_AA); a = fill(a, m, (185, 188, 192))
    a = fill(a, circ(300, 960, 70), (205, 208, 212)); a = fill(a, rect_mask(290, 930, 380, 960, 8), (225, 227, 230))
    save('shower_2026', a)
    b = wall.copy()
    b = fill(b, rect_mask(560, 0, 572, 90), (170, 168, 165))
    hp = np.array([[430, 110], [800, 110], [760, 150], [470, 150]], np.int32); m = np.zeros((H, W), np.float32); cv2.fillPoly(m, [hp], 1)
    b = fill(b, m, (165, 163, 160))
    b = shadow(b, rect_mask(300, 560, 400, 720, 6), 8, 8, 8, .25); b = fill(b, rect_mask(300, 560, 400, 720, 6), (172, 170, 166))
    for y in (605, 675): b = fill(b, circ(350, y, 22), (150, 148, 144))
    b = fill(b, rect_mask(520, 560, 534, 700, 6), (172, 170, 166))
    m = np.zeros((H, W), np.float32); cv2.ellipse(m, (527, 840), (40, 150), 0, 0, 360, 1, 5, cv2.LINE_AA); b = fill(b, m, (160, 158, 154))
    save('shower_2027', b)


def make_toilet():
    trav = plaster((222, 206, 186), 31, 8)
    trav += (noise(H, W, ((2, .7), (6, .3)), 32)[..., None] * 6)
    for y in range(0, H, 3):
        if rng.random() < .05: trav = line(trav, (0, y), (W, y), (205, 188, 168), 1, .5)
    trav = line(trav, (0, 420), (W, 420), (200, 185, 166), 2, .8)
    trav = line(trav, (0, 1010), (W, 1010), (200, 185, 166), 2, .8)
    # солнечный блик
    yy, xx = np.mgrid[0:H, 0:W]
    sun = ((xx + yy * .8 > 300) & (xx + yy * .8 < 700)).astype(np.float32)
    trav = trav * (1 + .18 * cv2.GaussianBlur(sun, (0, 0), 25)[..., None])
    # подвесной унитаз справа
    def toilet(img):
        m = np.zeros((H, W), np.float32); cv2.ellipse(m, (W + 40, 980), (230, 150), 0, 0, 360, 1, -1, cv2.LINE_AA)
        img = shadow(img, m, -14, 20, 20, .25); return fill(img, m, (244, 244, 242))
    a = toilet(trav.copy())
    a = fill(a, circ(330, 560, 22), (190, 192, 196)); a = fill(a, rect_mask(260, 560, 400, 572, 5), (190, 192, 196))
    a = fill(a, rect_mask(270, 575, 390, 650, 10), (248, 248, 246))
    a = fill(a, rect_mask(60, 830, 200, 1200, 12), (248, 248, 246), .9)
    m = np.zeros((H, W), np.float32); cv2.rectangle(m, (60, 830), (200, 1200), 1, 4); a = fill(a, m, (190, 192, 196))
    a = fill(a, rect_mask(240, 860, 280, 1200, 16), (250, 250, 250)); a = fill(a, rect_mask(254, 760, 266, 870), (250, 250, 250))
    save('toilet_2026', a)
    b = toilet(trav.copy())
    m = np.zeros((H, W), np.float32); cv2.rectangle(m, (300, 300), (560, 1150), 1, 3, cv2.LINE_AA); b = fill(b, m, (110, 100, 90), .6)
    b = line(b, (300, 700), (560, 700), (110, 100, 90), 3, .6)
    b = fill(b, rect_mask(420, 702, 556, 1147), (70, 68, 66))                 # открытая ниша
    b = fill(b, rect_mask(425, 860, 552, 870), (120, 118, 114))
    b = fill(b, rect_mask(440, 760, 530, 858, 8), (246, 246, 244))
    b = fill(b, rect_mask(470, 950, 500, 1140, 10), (175, 177, 180)); b = fill(b, rect_mask(482, 880, 488, 950), (190, 192, 196))
    door = np.array([[300, 702], [420, 702], [430, 1150], [300, 1147]], np.int32); m = np.zeros((H, W), np.float32); cv2.fillPoly(m, [door], 1)
    b = b * (1 - .06 * m[..., None])
    save('toilet_2027', b)


for f in (make_socket, make_skirting, make_vent, make_drain, make_shower, make_toilet):
    f()
print('ok')
