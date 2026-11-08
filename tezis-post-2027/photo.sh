#!/usr/bin/env bash
# Эскиз -> фото: img2img с небольшой силой, геометрия деталей сохраняется.
# bash photo.sh <папка эскизов> <папка вывода>
SK=${1:?}; OUT=${2:?}; mkdir -p "$OUT"
GEN="python3 $(dirname "$0")/../tezis-reel-starry/gen.py"
ST="architectural detail photography, photorealistic, natural soft daylight, high detail, sharp focus, realistic materials and shadows"
P_socket_2026="close-up photo of a glossy white plastic power socket with a thick white frame on a textured beige plaster wall"
P_socket_2027="close-up photo of a frameless flush power socket painted in the same beige color as the textured plaster wall, thin shadow gap around"
P_skirting_2026="photo of a white wall and light oak plank floor with a tall white skirting board"
P_skirting_2027="photo of a white wall and light oak plank floor with a recessed shadow gap skirting, thin dark shadow line, wall flush"
P_vent_2026="photo of a white plaster ceiling with a square white plastic bathroom exhaust fan grille with round vents, beige stone tile wall corner below"
P_vent_2027="photo of a white plaster ceiling with a minimalist round flush ventilation diffuser with a thin black shadow gap ring, beige stone tile wall corner below"
P_drain_2026="photo of a shower floor with large grey stone porcelain tiles and a square perforated stainless steel point drain, diagonal tile cuts"
P_drain_2027="photo of a walk-in shower floor with large grey stone porcelain tiles in one plane and a long narrow stainless linear drain along the back wall, glass panel edge"
P_shower_2026="photo of a shower wall with large grey stone porcelain tiles, chrome shower slide rail with round hand shower and metal hose, round chrome mixer, tiled niche"
P_shower_2027="photo of a shower wall with large grey stone porcelain tiles, ceiling mounted square brushed nickel rain shower head, brushed nickel thermostat plate with two knobs, slim hand shower with hose, tiled niche"
P_toilet_2026="photo of a bathroom with warm travertine wall tiles, chrome toilet paper holder with roll on the wall, toilet roll stand and white toilet brush on the floor, white wall hung toilet, sunlight"
P_toilet_2027="photo of a bathroom with warm travertine wall tiles, hidden flush storage niche with tiled door open showing toilet roll and steel toilet brush inside, white wall hung toilet, sunlight"
for n in socket skirting vent drain shower toilet; do for y in 2026 2027; do
  k="P_${n}_${y}"; f="$OUT/${n}_${y}.png"
  [ -f "$f" ] || $GEN img "$f" "${!k}, $ST" "$SK/${n}_${y}.png" 0.42 31 30 2>&1 | grep -E "^ok|Error"
done; done
echo done
