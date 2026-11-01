import sys, time, torch
from diffusers import AutoPipelineForImage2Image
from PIL import Image
torch.set_num_threads(4)
prompt, init, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
strengths = [float(s) for s in sys.argv[4].split(',')]
seed = int(sys.argv[5]); w, h = int(sys.argv[6]), int(sys.argv[7])
steps = int(sys.argv[8]) if len(sys.argv) > 8 else 4
pipe = AutoPipelineForImage2Image.from_pretrained("/home/user/models/sdxl-turbo", torch_dtype=torch.bfloat16, variant="fp16").to("cpu")
src = Image.open(init).convert("RGB").resize((w, h), Image.LANCZOS)
for st in strengths:
    t0 = time.time()
    img = pipe(prompt=prompt, image=src, num_inference_steps=steps, strength=st, guidance_scale=0.0, generator=torch.Generator().manual_seed(seed)).images[0]
    img.save(f"{prefix}_{int(st*100)}.png"); print("done", st, round(time.time() - t0, 1), "s", flush=True)
