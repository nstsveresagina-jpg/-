# Видео-сторис 1080×1920: сверху ролики (или фото с медленным наездом), поверх — прозрачный оверлей ov/ov_N.png
# usage: python3 build_video.py [N ...]
import subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
W, AH, FPS = 1080, 1260, 30          # зона видео над карточкой: 1080×1260
# сегмент: ('v', файл, начало, длительность, y) или ('p', фото, длительность, y); y — какая часть кадра по вертикали в центре (0..1)
STORIES = {
    1: [('p', '9942', 3.5, 0.62), ('v', 'v_120459', 12.5, 5.0, 0.32)],
    2: [('v', 'tg_06', 0.5, 3.5, 0.55), ('v', 'tg_08b', 2.0, 3.0, 0.60), ('p', '9924', 4.0, 0.70)],
    3: [('p', '9945', 4.5, 0.66), ('p', '9946', 3.5, 0.55)],
    4: [('v', 'tg_01', 4.0, 5.0, 0.45), ('p', '9929', 3.5, 0.30)],
    5: [('v', 'tg_20', 8.0, 3.0, 0.55), ('v', 'v_172013', 0.5, 4.5, 0.55), ('v', 'v_171013', 2.0, 3.0, 0.50)],
    6: [('v', 'v_164238', 6.0, 5.0, 0.50), ('v', 'tg_12', 0.2, 5.0, 0.55)],
    7: [('v', 'v_171231', 0.3, 4.5, 0.45), ('p', '9948', 4.0, 0.60)],
}
def seg_filter(i, seg):
    y = seg[-1]
    cover = f"scale={W}:{AH}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{AH}:(iw-{W})/2:(ih-{AH})*{y}"
    if seg[0] == 'v':
        return f"[{i}:v]fps={FPS},{cover},setsar=1,eq=saturation=1.08:contrast=1.03[s{i}]"
    n = int(seg[2] * FPS)   # фото: наезд 1.00 → 1.07 на увеличенной копии, чтобы не дрожало
    return (f"[{i}:v]scale={W*2}:{AH*2}:force_original_aspect_ratio=increase:flags=lanczos,crop={W*2}:{AH*2}:(iw-{W*2})/2:(ih-{AH*2})*{y},"
            f"zoompan=z='1+0.07*on/{n}':d={n}:x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':s={W}x{AH}:fps={FPS},setsar=1,eq=saturation=1.06[s{i}]")
def build(k):
    segs = STORIES[k]; args = ['ffmpeg', '-v', 'error', '-y']
    for seg in segs:
        if seg[0] == 'v': args += ['-ss', str(seg[2]), '-t', str(seg[3]), '-i', f'src/{seg[1]}.mp4']
        else: args += ['-i', f'img/{seg[1]}.jpg']   # одно изображение: zoompan сам делает d кадров
    ov = len(segs); args += ['-i', f'ov/ov_{k}.png']
    f = [seg_filter(i, s) for i, s in enumerate(segs)]
    f.append(''.join(f'[s{i}]' for i in range(len(segs))) + f'concat=n={len(segs)}:v=1:a=0[cat]')
    f.append(f"[cat]pad={W}:1920:0:0:color=0xFBF6EC[bg]")
    f.append(f"[bg][{ov}:v]overlay=0:0:format=auto,format=yuv420p[out]")
    args += ['-filter_complex', ';'.join(f), '-map', '[out]', '-r', str(FPS), '-c:v', 'libx264', '-preset', 'slow', '-crf', '19',
             '-profile:v', 'high', '-movflags', '+faststart', f'story_{k}.mp4']
    subprocess.run(args, check=True, stdin=subprocess.DEVNULL)
    print('story', k, 'done', flush=True)
for k in (map(int, sys.argv[1:]) if len(sys.argv) > 1 else STORIES): build(k)
