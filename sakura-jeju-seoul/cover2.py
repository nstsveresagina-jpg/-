# Обложка Reels 1080×1920: фото ханока с сакурой (Pinterest), кремовая карточка с текстом, всё в зоне 3:4 (y 240–1680).
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W, H = 1080, 1920
NAVY, ORANGE, RED, CREAM = (30, 43, 60), (247, 165, 32), (232, 87, 42), (251, 246, 236)
FH, FB = 'fonts/AdvakenSans.otf', 'fonts/Comfortaa-Light.ttf'
im = Image.open('cover_photo.jpg').convert('RGB'); s = max(W / im.width, H / im.height)
im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS); x = (im.width - W) // 2; y = (im.height - H) // 2
im = ImageEnhance.Color(im.crop((x, y, x + W, y + H))).enhance(1.08).convert('RGBA')

def shadow_box(box, r, op=110, blur=26, dy=12):
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).rounded_rectangle((box[0], box[1] + dy, box[2], box[3] + dy), r, fill=op)
    sh = Image.new('RGBA', (W, H), (20, 15, 25, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(blur))); im.alpha_composite(sh)
def ctext(d, txt, f, fill, y, x0=0, w=W):
    tw = f.getlength(txt); d.text((x0 + (w - tw) / 2, y), txt, font=f, fill=fill)

# logo pill on top
logo = Image.open('logo.png').convert('RGBA'); lh = 64; logo = logo.resize((int(logo.width * lh / logo.height), lh), Image.LANCZOS)
F = ImageFont.truetype(FH, 28); wj = F.getlength('JEJU '); tw = logo.width + 16 + wj + F.getlength('TRIP'); x0 = int((W - tw) / 2)
shadow_box((x0 - 28, 268, x0 + tw + 28, 356), 44, op=70, blur=16, dy=6)
d = ImageDraw.Draw(im); d.rounded_rectangle((x0 - 28, 268, x0 + tw + 28, 356), 44, fill=CREAM); im.alpha_composite(logo, (x0, 280))
d.text((x0 + logo.width + 16, 298), 'JEJU', font=F, fill=RED); d.text((x0 + logo.width + 16 + wj, 298), 'TRIP', font=F, fill=ORANGE)

# cream card
card = (90, 1060, 990, 1560)
shadow_box(card, 56)
glass = im.crop(card).filter(ImageFilter.GaussianBlur(18))
m = Image.new('L', glass.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, glass.width - 1, glass.height - 1), 56, fill=255)
im.paste(glass, card[:2], m)
ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ov).rounded_rectangle(card, 56, fill=CREAM + (232,)); im.alpha_composite(ov)
d = ImageDraw.Draw(im); cx, cw = card[0], card[2] - card[0]
d.rounded_rectangle((W / 2 - 34, card[1] + 54, W / 2 + 34, card[1] + 62), 4, fill=ORANGE)
ctext(d, '1–10 АПРЕЛЯ 2027 · 10 ДНЕЙ', ImageFont.truetype(FB, 34), NAVY, card[1] + 92, cx, cw)
ctext(d, 'САКУРА', ImageFont.truetype(FH, 150), NAVY, card[1] + 150, cx, cw)
ctext(d, 'ОТ ЧЕДЖУ ДО СЕУЛА', ImageFont.truetype(FH, 64), ORANGE, card[1] + 316, cx, cw)
ctext(d, 'Чеджу → Пусан → Кёнджу → Сеул', ImageFont.truetype(FB, 36), NAVY, card[1] + 412, cx, cw)
im.convert('RGB').save('cover.jpg', quality=95); im.convert('RGB').save('cover.png')
