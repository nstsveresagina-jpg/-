#!/usr/bin/env bash
# Генерация пар «2027» (txt2img) -> «2026» (img2img из той же картинки, чтобы совпадали стена и свет).
# bash pairs.sh <папка вывода>
set -e
G=${1:?out dir}; mkdir -p "$G"
GEN="python3 $(dirname "$0")/../tezis-reel-starry/gen.py"
STYLE="architectural detail photography, photorealistic, soft natural daylight, high detail, sharp focus, 85mm"
pair () { # name  prompt2027  prompt2026  strength
  [ -f "$G/$1_2027.png" ] || $GEN txt "$G/$1_2027.png" "$2, $STYLE" 17 24 832 1216 2>&1 | grep -E "^ok|Error"
  [ -f "$G/$1_2026.png" ] || $GEN img "$G/$1_2026.png" "$3, $STYLE" "$G/$1_2027.png" "$4" 18 30 2>&1 | grep -E "^ok|Error"
}
pair socket \
  "close-up photo of a modern frameless flush mounted power socket painted in the same warm beige color as the wall, sits perfectly flush with the textured beige microcement wall, minimal" \
  "close-up photo of a standard glossy white plastic power socket with a thick white frame sticking out from a textured beige microcement wall" 0.6
pair skirting \
  "close-up photo of the bottom of a warm white wall meeting a light oak herringbone floor with a recessed shadow gap skirting, thin dark shadow line, wall and floor meet flush, minimal" \
  "close-up photo of the bottom of a warm white wall meeting a light oak herringbone floor with a tall thick white MDF skirting board" 0.62
pair toilet \
  "photo of a bathroom wall with large warm travertine tiles and a hidden recessed storage niche flush with the tiles, its tiled door slightly open showing spare toilet rolls and a brushed steel toilet brush inside, wall hung toilet on the right, soft sunlight with plant shadows" \
  "photo of a bathroom wall with large warm travertine tiles, chrome toilet paper holder on the wall, freestanding wire toilet roll stand and white plastic toilet brush standing on the floor, wall hung toilet on the right, soft sunlight with plant shadows" 0.72
pair vent \
  "close-up photo looking up at a smooth warm white plaster ceiling with a minimalist round flush ventilation diffuser with a thin shadow gap ring, beige stone wall corner at the bottom" \
  "close-up photo looking up at a smooth warm white plaster ceiling with a square white plastic bathroom exhaust fan grille with round vents, beige stone wall corner at the bottom" 0.6
pair drain \
  "photo of a walk-in shower floor corner with large warm grey stone porcelain tiles laid in one plane, long narrow stainless linear drain along the wall, frameless glass panel edge" \
  "photo of a shower floor corner with large warm grey stone porcelain tiles, a square perforated chrome point drain in the middle with diagonal tile cuts around it" 0.65
pair shower \
  "photo of a walk-in shower wall with large warm grey stone porcelain tiles, concealed shower system: ceiling mounted square brushed nickel rain shower head, slim rectangular brushed nickel thermostat plate with two knobs, minimal hand shower, tiled niche with bottles" \
  "photo of a shower wall with large warm grey stone porcelain tiles, chrome shower slide rail with round hand shower and long hose, round chrome mixer with lever, tiled niche with bottles" 0.68
echo done
