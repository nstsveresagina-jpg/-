import sys, time, torch, numpy as np
from PIL import Image
from spandrel import ModelLoader
torch.set_num_threads(4)
src, out = sys.argv[1], sys.argv[2]
W, H = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (1920, 1080)
sd = torch.load('/home/user/models/esrgan/RealESRGAN_x4plus_anime_6B.pth', map_location='cpu', weights_only=True)
model = ModelLoader().load_from_state_dict(sd.get('params_ema', sd)).eval()
img = np.asarray(Image.open(src).convert('RGB')).astype(np.float32) / 255.0
x = torch.from_numpy(img).permute(2, 0, 1)[None]
t0 = time.time()
with torch.no_grad():
    y = model(x)
y = (y[0].permute(1, 2, 0).clamp(0, 1).numpy() * 255).round().astype(np.uint8)
Image.fromarray(y).resize((W, H), Image.LANCZOS).save(out)
print('upscaled', y.shape, round(time.time() - t0, 1), 's ->', out)
