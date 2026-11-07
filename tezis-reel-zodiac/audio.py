# Звук: только улучшение голоса, без добавления звуков.
# python3 audio.py src.mov out.wav
import json, subprocess, sys
src, out = sys.argv[1:3]
chain = ('highpass=f=80,afftdn=nf=-30:tn=1,'
         'equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.0:g=2.5,equalizer=f=9000:t=q:w=1.5:g=1,'
         'acompressor=threshold=-24dB:ratio=3:attack=8:release=150:makeup=4')
m = subprocess.run(['ffmpeg', '-hide_banner', '-i', src, '-vn', '-af', chain + ',loudnorm=I=-14:TP=-1:LRA=9:print_format=json',
                    '-f', 'null', '-'], capture_output=True, text=True).stderr
m = json.loads(m[m.rindex('{'):])
ln = (f"loudnorm=I=-14:TP=-1:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
      f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vn', '-af', chain + ',' + ln + ',alimiter=limit=0.89:level=false',
                '-ar', '48000', '-ac', '2', out], check=True)
print('measured', m['input_i'], '->', 'target -14')
