import subprocess, sys, json
S="/tmp/claude-0/-home-user--/c1d483ab-d94d-56fe-b8d8-24fe5041141f/scratchpad"; B=S+"/build2"
import os; os.makedirs(B,exist_ok=True)
DRAFT = "draft" in sys.argv
W,H = (540,960) if DRAFT else (1080,1920)
SO=1.0; TOTAL=37.13
D=lambda n:f"{S}/dl/{n}.mov"; U=lambda n:f"{S}/up/{n}.mov"
# (out_start, out_end, file, src_start, kind, speed)
segs=[
 (0.00, 4.18,D(9707),2.65,"talk",1),
 (4.18, 5.20,D(9817),5.0,"beat",1),
 (5.20, 7.31,D(9785),0.0,"talk",1),
 (7.31, 9.43,U(9749),0.0,"beat",1.96/2.12),
 (9.43,12.58,D(9787),3.4,"talk",1),
 (12.58,13.74,U(9761),0.0,"beat",1.11/1.16),
 (13.74,15.95,D(9744),0.9,"talk",1),
 (15.95,18.06,D(9732),1.0,"talk",1),
 (18.06,19.13,U(9755),0.0,"beat",1.0/1.07),
 (19.13,21.24,D(9775),0.9,"talk",1),
 (21.24,23.89,D(9801),0.0,"talk",1),
 (23.89,26.54,U(9796),0.0,"beat",2.37/2.65),
 (26.54,28.65,D(9803),2.3,"talk",1),
 (28.65,29.72,U(9819),0.0,"beat",0.99/1.07),
 (29.72,31.83,D(9810),9.2,"talk",1),
 (31.83,37.13,D(9821),0.3,"end",1),
]
voices=[(D(9707),2.65,0.00,4.18),(D(9785),0.0,5.20,2.11),(D(9787),3.4,9.43,3.15),(D(9744),0.9,13.74,2.21),
        (D(9732),1.0,15.95,2.11),(D(9775),0.9,19.13,2.11),(D(9801),0.0,21.24,2.65),(D(9803),2.3,26.54,2.11),(D(9810),9.2,29.72,2.11)]
def run(c): subprocess.run(c,check=True)
if "noseg" not in sys.argv:
  parts=[]
  for i,(a,b,f,ss,kind,sp) in enumerate(segs):
    d=b-a; out=f"{B}/seg{i:02d}.mp4"; parts.append(out)
    z={"talk":"(1.0+0.10*t/%f)"%d,"end":"(1.0+0.08*t/%f)"%d}.get(kind,"(1.0+0.14*exp(-9*t))")
    vf=(f"setpts=(PTS-STARTPTS)/{sp},scale=w='trunc(max({W},{H}*iw/ih)*{z}/2)*2':h=-2:eval=frame,"
        f"crop={W}:{H}:(iw-{W})/2:(ih-{H})/2,setsar=1,fps=30,format=yuv420p")
    if a in (4.18,):
        vf+=",eq=brightness='0.6*exp(-12*t)':eval=frame"
    if kind=="end":
        pass
    run(["ffmpeg","-v","error","-y","-ss",str(ss),"-t",str(d*sp+0.15),"-i",f,"-an","-vf",vf,"-t",f"{d:.3f}",
         "-c:v","libx264","-preset","veryfast" if DRAFT else "medium","-crf","17","-r","30",out])
  open(B+"/list.txt","w").write("".join(f"file '{p}'\n" for p in parts))
  run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",B+"/list.txt","-c","copy",B+"/video.mp4"])
  duck="+".join(f"between(t,{o-0.1:.2f},{o+d:.2f})" for _,_,o,d in voices)
  inputs=["-ss",str(SO),"-t",str(TOTAL),"-i",S+"/src/song.wav"]
  fc=[f"[0:a]volume='if({duck},0.3,1)':eval=frame,afade=t=out:st={TOTAL-2.2:.2f}:d=2.2[m]"]
  for k,(f,ss,o,d) in enumerate(voices):
    inputs+=["-ss",str(ss),"-t",str(d),"-i",f]; ms=int(o*1000)
    fc.append(f"[{k+1}:a]aformat=sample_rates=44100:channel_layouts=stereo,highpass=f=120,acompressor=threshold=-24dB:ratio=4:makeup=4,volume=2.0,afade=t=in:d=0.05,afade=t=out:st={d-0.12:.2f}:d=0.12,adelay={ms}|{ms}[v{k}]")
  fc.append("[m]"+"".join(f"[v{k}]" for k in range(len(voices)))+f"amix=inputs={len(voices)+1}:normalize=0,alimiter=limit=0.9,loudnorm=I=-14:TP=-1.0[a]")
  run(["ffmpeg","-v","error","-y",*inputs,"-filter_complex",";".join(fc),"-map","[a]","-t",str(TOTAL),"-ar","44100",B+"/audio.wav"])
  # faces on the edited picture (before text)
  run(["/home/user/venvs/fw/bin/python","-I",S+"/tools/faces.py",B+"/video.mp4",B+"/faces.json"])
run(["python3",S+"/tools/kinetic2.py",B+"/faces.json",S+"/tools/subs2.ass"])
out = S+"/draft2.mp4" if DRAFT else "/home/user/-/montage/montage.mp4"
run(["ffmpeg","-v","error","-y","-i",B+"/video.mp4","-i",B+"/audio.wav","-vf",f"ass={S}/tools/subs2.ass:fontsdir=/usr/share/fonts/opentype/inter",
     "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart","-shortest",out])
print(out)
