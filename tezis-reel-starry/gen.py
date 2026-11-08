# Генерация кадров комнаты SDXL 1.0 на CPU (лицензия CreativeML Open RAIL++-M, коммерческое использование разрешено).
# python3 gen.py txt  out.png "prompt" [seed] [steps] [w] [h]
# python3 gen.py img  out.png "prompt" init.png strength [seed] [steps]
# python3 gen.py inp  out.png "prompt" init.png mask.png strength [seed] [steps]  (белое в маске - дорисовать)
import sys, time, torch
from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline, StableDiffusionXLInpaintPipeline, DPMSolverMultistepScheduler
from PIL import Image

M = '/home/user/models/sdxl-base'
NEG = ('cartoon, illustration, painting, drawing, render artifacts, blurry, lowres, distorted, deformed, text, watermark, '
       'logo, people, person, extra windows, fisheye, oversaturated')
DT = torch.bfloat16
torch.set_num_threads(4)
mode, out, prompt = sys.argv[1:4]
t0 = time.time()
if mode == 'txt':
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 7
    steps = int(sys.argv[5]) if len(sys.argv) > 5 else 22
    w = int(sys.argv[6]) if len(sys.argv) > 6 else 768
    h = int(sys.argv[7]) if len(sys.argv) > 7 else 1344
    p = StableDiffusionXLPipeline.from_pretrained(M, torch_dtype=DT, variant='fp16', use_safetensors=True)
    p.scheduler = DPMSolverMultistepScheduler.from_config(p.scheduler.config, use_karras_sigmas=True)
    img = p(prompt, negative_prompt=NEG, num_inference_steps=steps, guidance_scale=6.0, width=w, height=h,
            generator=torch.Generator().manual_seed(seed)).images[0]
elif mode == 'inp':
    init = Image.open(sys.argv[4]).convert('RGB'); mask = Image.open(sys.argv[5]).convert('L')
    strength = float(sys.argv[6])
    seed = int(sys.argv[7]) if len(sys.argv) > 7 else 7
    steps = int(sys.argv[8]) if len(sys.argv) > 8 else 30
    p = StableDiffusionXLInpaintPipeline.from_pretrained(M, torch_dtype=DT, variant='fp16', use_safetensors=True)
    p.scheduler = DPMSolverMultistepScheduler.from_config(p.scheduler.config, use_karras_sigmas=True)
    img = p(prompt, negative_prompt=NEG, image=init, mask_image=mask, strength=strength, num_inference_steps=steps,
            guidance_scale=6.5, width=init.width, height=init.height, generator=torch.Generator().manual_seed(seed)).images[0]
    # вне маски оставляем исходные пиксели, по краю - мягкий переход
    from PIL import ImageFilter
    m = mask.filter(ImageFilter.GaussianBlur(6))
    img = Image.composite(img, init, m)
else:
    init = Image.open(sys.argv[4]).convert('RGB')
    strength = float(sys.argv[5])
    seed = int(sys.argv[6]) if len(sys.argv) > 6 else 7
    steps = int(sys.argv[7]) if len(sys.argv) > 7 else 30
    p = StableDiffusionXLImg2ImgPipeline.from_pretrained(M, torch_dtype=DT, variant='fp16', use_safetensors=True)
    p.scheduler = DPMSolverMultistepScheduler.from_config(p.scheduler.config, use_karras_sigmas=True)
    img = p(prompt, negative_prompt=NEG, image=init, strength=strength, num_inference_steps=steps, guidance_scale=6.0,
            generator=torch.Generator().manual_seed(seed)).images[0]
img.save(out)
print('ok', out, img.size, round(time.time() - t0), 's')
