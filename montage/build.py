import subprocess, sys, os
S="/tmp/claude-0/-home-user--/c1d483ab-d94d-56fe-b8d8-24fe5041141f/scratchpad"; B=S+"/build"
DRAFT = len(sys.argv)>1 and sys.argv[1]=="draft"
W,H = (540,960) if DRAFT else (1080,1920)
SO=1.0  # song offset
# (out_start, out_end, clip, src_start, kind, speed)
segs=[
 (0.00, 4.18,"9707",2.65,"talk",1),
 (4.18, 5.20,"9817",5.0,"beat",1),
 (5.20, 6.22,"9737",0.0,"beat",1),
 (6.22, 7.31,"9789",13.0,"beat",1),
 (7.31, 8.36,"9723",9.0,"beat",1),
 (8.36,11.00,"9787",3.8,"talk",1),
 (11.00,12.07,"9813",12.0,"beat",1),
 (12.07,14.35,"9732",1.0,"talk",1),
 (14.35,15.42,"9739",2.0,"beat",1),
 (15.42,16.48,"9735",2.5,"beat",1),
 (16.48,19.13,"9801",0.0,"talk",1),
 (19.13,21.24,"9810",9.2,"talk",1),
 (21.24,22.31,"9750",8.0,"beat",1),
 (22.31,23.36,"9807",7.5,"beat",1),
 (23.36,24.43,"9722",1.5,"beat",1),
 (24.43,25.47,"9813",16.0,"beat",1),
 (25.47,27.07,"9772",6.9,"beat",1),
 (27.07,30.00,"9707",0.0,"end",0.7),
]
def run(c): subprocess.run(c,check=True)
parts=[]
for i,(a,b,clip,ss,kind,sp) in enumerate(segs):
    d=b-a; out=f"{B}/seg{i:02d}.mp4"; parts.append(out)
    srcd=d*sp
    if kind=="talk": z="(1.0+0.10*t/%f)"%d          # slow push-in
    elif kind=="end": z="(1.0+0.06*t/%f)"%d
    else: z="(1.0+0.14*exp(-9*t))"                   # punch on the beat
    vf=(f"setpts=(PTS-STARTPTS)/{sp},scale=w='trunc({W}*{z}/2)*2':h=-2:eval=frame,"
        f"crop={W}:{H}:(iw-{W})/2:(ih-{H})/2,setsar=1,fps=30,format=yuv420p")
    if kind=="beat" and a in (4.18,21.24):  # white flash on the drops
        vf+=f",eq=brightness='0.6*exp(-12*t)':eval=frame"
    run(["ffmpeg","-v","error","-y","-ss",str(ss),"-t",str(srcd+0.1),"-i",f"{S}/dl/{clip}.mov","-an",
         "-vf",vf,"-t",f"{d:.3f}","-c:v","libx264","-preset","veryfast" if DRAFT else "medium","-crf","18","-r","30",out])
open(B+"/list.txt","w").write("".join(f"file '{p}'\n" for p in parts))
run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",B+"/list.txt","-c","copy",B+"/video.mp4"])
# --- audio: song + live voices, music ducked under voices
voices=[  # (clip, src_start, out_start, dur, gain)
 ("9707",2.65,0.0,4.18,2.2),("9787",3.8,8.36,2.64,2.0),("9732",1.0,12.07,2.28,2.0),
 ("9801",0.0,16.48,2.65,2.0),("9810",9.2,19.13,2.11,2.0),("9798",9.9,25.7,2.9,2.4)]
duck="+".join(f"between(t,{o-0.1:.2f},{o+d:.2f})" for _,_,o,d,_ in voices)
inputs=["-ss",str(SO),"-t","30","-i",S+"/src/song.wav"]; fc=[]
fc.append(f"[0:a]volume='if({duck},0.28,1)':eval=frame,afade=t=out:st=28.3:d=1.7[m]")
for k,(c,ss,o,d,g) in enumerate(voices):
    inputs+=["-ss",str(ss),"-t",str(d),"-i",f"{S}/dl/{c}.mov"]
    ms=int(o*1000)
    fc.append(f"[{k+1}:a]aformat=sample_rates=44100:channel_layouts=stereo,highpass=f=120,acompressor=threshold=-24dB:ratio=4:makeup=4,volume={g},afade=t=in:d=0.05,afade=t=out:st={d-0.12:.2f}:d=0.12,adelay={ms}|{ms}[v{k}]")
fc.append("[m]"+"".join(f"[v{k}]" for k in range(len(voices)))+f"amix=inputs={len(voices)+1}:normalize=0,alimiter=limit=0.9,loudnorm=I=-14:TP=-1.0[a]")
run(["ffmpeg","-v","error","-y",*inputs,"-filter_complex",";".join(fc),"-map","[a]","-t","30","-ar","44100",B+"/audio.wav"])
# --- final: burn subtitles
out = S+"/draft.mp4" if DRAFT else "/home/user/-/montage/montage_30s.mp4"
run(["ffmpeg","-v","error","-y","-i",B+"/video.mp4","-i",B+"/audio.wav","-vf",f"ass={S}/tools/subs.ass:fontsdir=/usr/share/fonts/opentype/inter",
     "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart","-shortest",out])
print(out)
