# Working preferences

## Tools and cost
- Use only free plugins, tools, models and functions. Never suggest or install anything paid: no paid accounts, credits or subscriptions. If something might cost money (or its license limits commercial use), say so plainly and offer a free alternative.

## Language
- The user writes in Russian; answer in Russian.

# Project: cartoon "Бабушка и внуки"
- Goal: a warm, nostalgic cartoon about a grandmother and her grandchildren.
- Target look: the drawing style of late-1970s/80s Soviet cel animation (as in "Зима в Простоквашино"): night winter scene, big snowy blue spruce painted like gouache, paper-chain garlands, apples, a lamp, big snowflakes, characters with clean dark ink outlines and flat colours. Use the style only; never copy that film's characters, scenes or music.
- Characters (original): grandma in a red flowered headscarf, round glasses, coat with a fur collar; granddaughter with chestnut hair in a pink knitted hat and red coat; grandson in a fur ushanka, green coat, yellow scarf.
- The user found code-drawn frames too crude and SDXL-on-CPU frames too blurry. Best quality path: a free GPU (Kaggle / Google Colab) and a LoRA trained on reference frames.

## Environment notes (cloud container is ephemeral)
- `setup.sh` reinstalls the free toolchain (voices, music tools, Stable Diffusion, upscaler).
- Network allowlist must include: huggingface.co, *.huggingface.co, models.silero.ai, api.openverse.org, freesound.org, cdn.freesound.org, upload.wikimedia.org.
- Voices: Piper ru_RU (irina, denis, dmitri, ruslan) — free incl. commercial (check each voice's licence); Silero v4_ru — free for non-commercial use only.
- Image models: stabilityai/sdxl-turbo and stable-diffusion-xl-base-1.0 (check the Stability AI licence before any commercial use); upscaler RealESRGAN_x4plus_anime_6B (BSD-3).
