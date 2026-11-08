# Очистка речи нейросетью DeepFilterNet (MIT/Apache-2.0): шум и гул пустых комнат.
# /home/user/venvs/dfn/bin/python dfn_clean.py in48k.wav out.wav [atten_db]
import sys
import soundfile as sf
import torch
from df.enhance import enhance, init_df

src, out = sys.argv[1:3]
atten = float(sys.argv[3]) if len(sys.argv) > 3 else 18.0  # не глушим полностью, чтобы голос звучал живо
model, state, _ = init_df(model_base_dir=sys.argv[4] if len(sys.argv) > 4 else None)
audio, sr = sf.read(src, dtype='float32', always_2d=True)
assert sr == state.sr(), f'нужно {state.sr()} Гц'
x = torch.from_numpy(audio.T.mean(0, keepdims=True))
y = enhance(model, state, x, atten_lim_db=atten)
sf.write(out, y.squeeze(0).numpy(), sr)
print('ok', sr)
