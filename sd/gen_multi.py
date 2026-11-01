import sys, time, torch
from diffusers import AutoPipelineForText2Image
torch.set_num_threads(4)
prompt, prefix = sys.argv[1], sys.argv[2]
seeds = [int(s) for s in sys.argv[3].split(',')]
w, h = int(sys.argv[4]), int(sys.argv[5])
pipe = AutoPipelineForText2Image.from_pretrained("/home/user/models/sdxl-turbo", torch_dtype=torch.bfloat16, variant="fp16").to("cpu")
for s in seeds:
    t0 = time.time()
    img = pipe(prompt=prompt, num_inference_steps=4, guidance_scale=0.0, width=w, height=h, generator=torch.Generator().manual_seed(s)).images[0]
    img.save(f"{prefix}_{s}.png"); print("done", s, round(time.time() - t0, 1), "s", flush=True)
