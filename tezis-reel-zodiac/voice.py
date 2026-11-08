# Голос: DeepFilterNet уже убрал шум и гул (dfn_clean.py), здесь тембр и громкость.
# python3 voice.py dfn.wav out.wav
import json, subprocess, sys
src, out = sys.argv[1:3]
chain = ('highpass=f=90,'
         'equalizer=f=450:t=q:w=1.0:g=-4,'      # убираем «коробочный» гул пустой комнаты
         'equalizer=f=220:t=q:w=1.2:g=-1.5,'
         'equalizer=f=3500:t=q:w=1.2:g=3.5,'    # разборчивость
         'treble=g=3:f=8000,'                   # воздух, чтобы не было глухо
         'deesser=i=0.35,'
         'acompressor=threshold=-22dB:ratio=3:attack=6:release=120:makeup=3')
m = subprocess.run(['ffmpeg', '-hide_banner', '-i', src, '-af', chain + ',loudnorm=I=-14:TP=-1:LRA=8:print_format=json',
                    '-f', 'null', '-'], capture_output=True, text=True).stderr
m = json.loads(m[m.rindex('{'):])
ln = (f"loudnorm=I=-14:TP=-1:LRA=8:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
      f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', chain + ',' + ln + ',volume=0.9dB,alimiter=limit=0.89:level=false',
                '-ar', '48000', '-ac', '2', out], check=True)
print('ok')
