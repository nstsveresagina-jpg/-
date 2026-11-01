#!/usr/bin/env bash
# Reinstall the free cartoon toolchain in a fresh cloud session.
set -e
apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq rhvoice rhvoice-russian fluid-soundfont-gm fluidsynth sox libsox-fmt-all
pip install -q mido pydub audioop-lts pedalboard soundfile piper-tts panns-inference librosa diffusers transformers accelerate safetensors spandrel
pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cpu
mkdir -p /home/user/models/voices /home/user/models/esrgan
B=https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU
for v in irina denis dmitri ruslan; do n=ru_RU-$v-medium; curl -sSL -o /home/user/models/voices/$n.onnx $B/$v/medium/$n.onnx; curl -sSL -o /home/user/models/voices/$n.onnx.json $B/$v/medium/$n.onnx.json; done
curl -sSL -o /home/user/models/esrgan/RealESRGAN_x4plus_anime_6B.pth https://huggingface.co/amd/realesrgan-x4plus-anime-6b/resolve/main/RealESRGAN_x4plus_anime_6B.pth
python3 - <<'PY'
from huggingface_hub import snapshot_download
for repo, d in [("stabilityai/sdxl-turbo", "sdxl-turbo"), ("stabilityai/stable-diffusion-xl-base-1.0", "sdxl-base")]:
    snapshot_download(repo, allow_patterns=["*.json", "*.txt", "tokenizer*/*", "text_encoder/model.fp16.safetensors", "text_encoder_2/model.fp16.safetensors", "unet/diffusion_pytorch_model.fp16.safetensors", "vae/diffusion_pytorch_model.fp16.safetensors"], local_dir=f"/home/user/models/{d}")
PY
# animation libraries (all free / open source)
npm i -g hyperframes
mkdir -p /home/user/remotion-test && cd /home/user/remotion-test && [ -f package.json ] || npm init -y >/dev/null
npm i remotion @remotion/cli react react-dom animejs @react-spring/web pixi.js p5 paper
echo "setup done"
