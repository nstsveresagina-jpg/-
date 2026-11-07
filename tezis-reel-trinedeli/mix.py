# Звук: голос из клипа (чистка + громкость) + музыка из примера без голосов (Demucs).
# Как в примере: сначала энергичный трек, на «Тише, тише» короткий обрыв и переход на спокойный.
# python3 mix.py clip.mov no_vocals.wav out.wav
import json, subprocess, sys
clip, music, out = sys.argv[1:4]
SWITCH = 2.30          # в клипе: «Тише, тише» (2.35 с)
CALM0 = 4.40           # в примере: начало спокойного трека (после паузы 3.8-4.4 с)
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', clip],
                           capture_output=True, text=True).stdout)
calm_len = dur - SWITCH
voice = ('highpass=f=80,afftdn=nf=-30:tn=1,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.0:g=2.5,'
         'equalizer=f=9000:t=q:w=1.5:g=1,acompressor=threshold=-24dB:ratio=3:attack=8:release=150:makeup=4,'
         'loudnorm=I=-15:TP=-2:LRA=7')
fmt = 'aresample=48000,aformat=channel_layouts=stereo'
# шаг 1: музыкальная подложка отдельным файлом (в одном графе ветки не дожидаются друг друга)
bed = out + '.music.wav'
fm = (f"[0:a]{fmt},asplit=2[m1][m2];"
      # энергичный: с начала трека, к «Тише» быстро уходит
      f"[m1]atrim=0:{SWITCH},asetpts=PTS-STARTPTS,afade=t=out:st={SWITCH - 0.22}:d=0.22[e];"
      # спокойный: с его начала, в конце мягко затихает
      f"[m2]atrim={CALM0}:{CALM0 + calm_len},asetpts=PTS-STARTPTS,afade=t=in:d=0.12,"
      f"afade=t=out:st={calm_len - 1.4}:d=1.4,volume=1.15[c];"
      f"[e][c]concat=n=2:v=0:a=1,loudnorm=I=-24:TP=-3:LRA=14[m]")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', music, '-filter_complex', fm, '-map', '[m]', bed], check=True)
# шаг 2: голос + музыка, музыка приглушается под речью
fc = (f"[0:a]{voice},{fmt},asplit=2[v][sc];[1:a]{fmt}[m];"
      f"[m][sc]sidechaincompress=threshold=0.05:ratio=2.5:attack=20:release=350[md];"
      f"[v][md]amix=inputs=2:normalize=0:duration=first[mix]")
tmp = out + '.tmp.wav'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', clip, '-i', bed, '-filter_complex', fc, '-map', '[mix]', tmp], check=True)
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', tmp, '-af', 'loudnorm=I=-14:TP=-1:LRA=9:print_format=json', '-f', 'null', '-'],
                   capture_output=True, text=True).stderr
j = json.loads(r[r.rindex('{'):])
ln = (f"loudnorm=I=-14:TP=-1:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
      f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,alimiter=limit=0.89:level=false")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', ln, out], check=True)
print('ok')
