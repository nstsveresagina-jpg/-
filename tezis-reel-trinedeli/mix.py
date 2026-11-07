# Звук: голос из клипа (чистка + громкость) + музыка из примера без голосов (Demucs), приглушается под речью.
# python3 mix.py clip.mov no_vocals.wav out.wav [music_start]
import json, subprocess, sys
clip, music, out = sys.argv[1:4]
m0 = float(sys.argv[4]) if len(sys.argv) > 4 else 11.5
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', clip],
                           capture_output=True, text=True).stdout)
voice = ('highpass=f=80,afftdn=nf=-30:tn=1,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.0:g=2.5,'
         'equalizer=f=9000:t=q:w=1.5:g=1,acompressor=threshold=-24dB:ratio=3:attack=8:release=150:makeup=4,'
         'loudnorm=I=-15:TP=-2:LRA=7')
fc = (f"[0:a]{voice},aresample=48000,aformat=channel_layouts=stereo,asplit=2[v][sc];"
      f"[1:a]atrim={m0}:{m0 + dur},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
      f"loudnorm=I=-25:TP=-3:LRA=11,afade=t=in:d=0.15,afade=t=out:st={dur - 0.8}:d=0.8[m];"
      f"[m][sc]sidechaincompress=threshold=0.05:ratio=3:attack=20:release=300[md];"
      f"[v][md]amix=inputs=2:normalize=0:duration=first[mix]")
tmp = out + '.tmp.wav'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', clip, '-i', music, '-filter_complex', fc, '-map', '[mix]', tmp], check=True)
# итог -14 LUFS в два прохода
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', tmp, '-af', 'loudnorm=I=-14:TP=-1:LRA=9:print_format=json', '-f', 'null', '-'],
                   capture_output=True, text=True).stderr
j = json.loads(r[r.rindex('{'):])
ln = (f"loudnorm=I=-14:TP=-1:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
      f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,alimiter=limit=0.89:level=false")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', ln, out], check=True)
print('ok')
