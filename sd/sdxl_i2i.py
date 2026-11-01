import sys, time, torch
from diffusers import StableDiffusionXLImg2ImgPipeline
from PIL import Image
torch.set_num_threads(4)
prompt, neg, init, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
strength, seed, steps = float(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])
w, h = 1344, 768
pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained("/home/user/models/sdxl-base", torch_dtype=torch.bfloat16, variant="fp16").to("cpu")
src = Image.open(init).convert("RGB").resize((w, h), Image.LANCZOS)
t0 = time.time()
img = pipe(prompt=prompt, negative_prompt=neg, image=src, strength=strength, num_inference_steps=steps, guidance_scale=6.5, generator=torch.Generator().manual_seed(seed)).images[0]
img.save(out); print("done", out, round(time.time() - t0, 1), "s", flush=True)
