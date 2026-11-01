import sys, time, torch
from diffusers import AutoPipelineForText2Image
torch.set_num_threads(4)
prompt, out, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
w = int(sys.argv[4]) if len(sys.argv) > 4 else 896
h = int(sys.argv[5]) if len(sys.argv) > 5 else 512
steps = int(sys.argv[6]) if len(sys.argv) > 6 else 4
t0 = time.time()
pipe = AutoPipelineForText2Image.from_pretrained("/home/user/models/sdxl-turbo", torch_dtype=torch.bfloat16, variant="fp16")
pipe.to("cpu")
print("loaded", round(time.time() - t0, 1), "s", flush=True)
g = torch.Generator().manual_seed(seed)
img = pipe(prompt=prompt, num_inference_steps=steps, guidance_scale=0.0, width=w, height=h, generator=g).images[0]
img.save(out)
print("done", out, round(time.time() - t0, 1), "s")
