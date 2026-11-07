# Что установить на ПК (всё бесплатно)

## 1. Плагины Claude (каталог Anthropic Directory)
В Claude Code: команда `/plugin` → вкладка Discover → найти по названию → Install.
В приложении Claude Desktop: раздел плагинов → поиск по названию.

| Плагин | Зачем |
|---|---|
| animation-studio | рисованные мультики кодом + музыка, MP4 |
| Remotion | навыки по видео на React (Remotion) |
| Motion Reel | анимация и 3D кодом, губы под голос (без платного дополнения motion-reel-voice) |
| video-shotcraft | кинематографичные ролики на Remotion |
| video-cleanup | чистка звука и картинки, логотип, титры |
| image-generation | как правильно описывать картинки для нейросетей |
| Task Observer | запоминает ваши правила в CLAUDE.md |
| Headroom | чтение больших файлов по частям |

Отключены в этом проекте (файл `.claude/settings.json`), чтобы не тратить лимит: small-business, marketing, operations, claude-code-setup. Включить обратно: `claude plugin enable <имя>@synced --scope project`.

## 2. Плагин с GitHub (на ПК память сохраняется)
- claude-mem (Apache-2.0): в Claude Code выполнить
  `/plugin marketplace add thedotmack/claude-mem`, затем `/plugin install claude-mem`

## 3. Программы и модели (ставит Claude по `setup.sh`; для Windows будет отдельная версия)
- Озвучка: Chatterbox (MIT, ваш голос), Piper (голоса Денис, Дмитрий — CC0)
- Распознавание речи: faster-whisper (MIT)
- Музыка и звук: Tone.js, FluidSynth + FluidR3, SoX, Pedalboard
- Анимация: HyperFrames, Remotion*, anime.js, React Spring, PixiJS, p5.js, Paper.js, tsParticles, GL Transitions, three.js, Matter.js, Rapier
- Картинки: Stable Diffusion XL, Real-ESRGAN (увеличение)
- С видеокартой NVIDIA: ComfyUI + comfyui-mcp, ToonCrafter, AnimateDiff, RIFE, обучение стиля (kohya)

\* Remotion бесплатен для частных лиц и команд до 3 человек.
