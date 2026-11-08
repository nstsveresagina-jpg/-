# Обложка Reels 1080×1920: яркое фото без затемнения, крупный заголовок Advaken на всю ширину, текст в зоне 3:4 (y 240–1680).
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W, H = 1080, 1920
NAVY, ORANGE, RED, WHITE, CREAM = (30, 43, 60), (247, 165, 32), (232, 87, 42), (255, 255, 255), (251, 246, 236)
FH, FB = 'fonts/AdvakenSans.otf', 'fonts/Comfortaa-Light.ttf'
im = Image.open('cover_photo.jpg').convert('RGB'); s = max(W / im.width, H / im.height)
im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS); x = (im.width - W) // 2; y = (im.height - H) // 2
im = ImageEnhance.Color(im.crop((x, y, x + W, y + H))).enhance(1.10).convert('RGBA')
def ctext(txt, f, size, fill, y, track=0, maxw=980, shadow=0.75):
    F = ImageFont.truetype(f, size)
    while sum(F.getlength(c) for c in txt) + track * (len(txt) - 1) > maxw: size -= 2; F = ImageFont.truetype(f, size)
    w = sum(F.getlength(c) for c in txt) + track * (len(txt) - 1)
    lay = Image.new('RGBA', (W, size * 2), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay); x = (W - w) / 2
    for c in txt: dl.text((x, size // 3), c, font=F, fill=fill); x += F.getlength(c) + track
    a = lay.split()[3]
    for r, op in ((26, shadow), (8, shadow * .8)):
        s_ = Image.new('RGBA', lay.size, (5, 12, 25, 0)); s_.putalpha(a.filter(ImageFilter.GaussianBlur(r)).point(lambda v, op=op: int(v * op))); im.alpha_composite(s_, (0, y - size // 3 + 5))
    im.alpha_composite(lay, (0, y - size // 3))
logo = Image.open('logo.png').convert('RGBA'); lh = 64; logo = logo.resize((int(logo.width * lh / logo.height), lh), Image.LANCZOS)
d = ImageDraw.Draw(im); F = ImageFont.truetype(FH, 28); wj = F.getlength('JEJU '); tw = logo.width + 16 + wj + F.getlength('TRIP'); x0 = int((W - tw) / 2)
d.rounded_rectangle((x0 - 28, 268, x0 + tw + 28, 356), 44, fill=CREAM); im.alpha_composite(logo, (x0, 280))
d.text((x0 + logo.width + 16, 298), 'JEJU', font=F, fill=RED); d.text((x0 + logo.width + 16 + wj, 298), 'TRIP', font=F, fill=ORANGE)
ctext('БАЛИ', FH, 200, WHITE, 420)
ctext('РОЖДЕСТВО И НОВЫЙ ГОД', FH, 76, ORANGE, 650)
ctext('два праздника в одном путешествии', FB, 44, WHITE, 780, shadow=1.0)
ctext('23.12.2026 – 03.01.2027 · 11 дней · мини-группа', FB, 38, WHITE, 1500, shadow=1.0)
im.convert('RGB').save('cover.jpg', quality=95)
