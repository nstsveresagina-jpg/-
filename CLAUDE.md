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
- Voices (checked licences): Piper ru_RU denis and dmitri — CC0, OK for any use; Piper irina — dataset licence unknown; Piper ruslan — CC BY-NC-SA (non-commercial only); Silero v4_ru — non-commercial only; several RHVoice voices are non-commercial too (see /usr/share/RHVoice/voices/*/Readme); Chatterbox — MIT. For anything monetised use denis, dmitri or Chatterbox.
- Animation libraries: Remotion (free for individuals and companies of up to 3 people; larger companies need a paid licence), HyperFrames (Apache-2.0), anime.js (MIT), React Spring (MIT), PixiJS (MIT), p5.js (LGPL-2.1), Paper.js (MIT), tsParticles (MIT), GL Transitions (MIT), three.js (MIT), Matter.js (MIT), Rapier 2D/3D (Apache-2.0), Tone.js (MIT).
- Speech: faster-whisper (MIT) for recognition; pass audio as a numpy array (librosa, 16 kHz) because file decoding via PyAV fails here. Chatterbox TTS (MIT, multilingual incl. Russian) lives in /home/user/venvs/chatterbox; it adds an inaudible Perth watermark to its output; on CPU a short line takes several minutes.
- Image models: stabilityai/sdxl-turbo and stable-diffusion-xl-base-1.0 (SDXL base: CreativeML Open RAIL++-M, commercial use allowed with use restrictions; SDXL-Turbo: Stability AI Community Licence, free for non-commercial use and for commercial use under USD 1M annual revenue); upscaler RealESRGAN_x4plus_anime_6B (BSD-3).
