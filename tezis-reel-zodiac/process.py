# Покадрово: единый фильтр + ретушь лиц. python3 process.py src.mov face_landmarker.task out.mp4
import sys, subprocess, numpy as np
from retouch import Retoucher, make_grade, apply_grade
from shots import shot_gains, gains_at
src, model, out = sys.argv[1:4]
W, H, FPS = 1080, 1920, 30
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout)
rt = Retoucher(model)
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
n = 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    f = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    t = n / FPS
    g = f.copy()  # без фильтра: цвет как в исходнике
    enc.stdin.write(rt.retouch(g, int(t * 1000)).tobytes())
    n += 1
    if n % 150 == 0: print(n, flush=True)
enc.stdin.close(); enc.wait(); print('frames', n)
