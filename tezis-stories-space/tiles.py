# Вырезает 9 комнат из каждой исходной картинки: python3 tiles.py
from PIL import Image
import os
here = os.path.dirname(os.path.abspath(__file__))
cols = [48, 385, 722]; rows = [261, 656, 1038]; W, H = 316, 300
for name in ['color', 'shades', 'lines', 'bigger', 'light']:
    im = Image.open(f'{here}/src/{name}.jpg').convert('RGB')
    for r, y in enumerate(rows):
        for c, x in enumerate(cols):
            # отступ 6px внутрь, чтобы убрать скругления и фон исходника
            im.crop((x+6, y+6, x+W-6, y+H-6)).save(f'{here}/tiles/{name}_{r*3+c+1}.jpg', quality=97)
print('ok')
