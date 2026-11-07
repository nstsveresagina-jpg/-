# Kinetic "sticker" text: every word pops in on its spoken timestamp, tilted, stacked, coloured.
import random
random.seed(7)
S="/tmp/claude-0/-home-user--/c1d483ab-d94d-56fe-b8d8-24fe5041141f/scratchpad"
def ts(t): return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
hdr="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Y,Inter ExtraBold,100,&H00111111,&H00111111,&H0000E5FF,&H00000000,-1,0,0,0,100,100,2,0,3,16,0,5,0,0,0,1
Style: P,Inter ExtraBold,100,&H00FFFFFF,&H00FFFFFF,&H00A020FF,&H00000000,-1,0,0,0,100,100,2,0,3,16,0,5,0,0,0,1
Style: W,Inter ExtraBold,100,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00A020FF,-1,0,0,0,100,100,2,0,1,9,9,5,0,0,0,1
Style: K,Inter ExtraBold,100,&H0000E5FF,&H0000E5FF,&H00000000,&H00000000,-1,0,0,0,100,100,2,0,1,10,8,5,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev=[]
def word(t0,t1,txt,x,y,style,size=100,rot=0,shake=False,layer=1):
    dur=int((t1-t0)*1000)
    a=(f"{{\\pos({x},{y})\\fs{size}\\frz{rot}\\fscx0\\fscy0"
       f"\\t(0,90,\\fscx128\\fscy128)\\t(90,190,\\fscx100\\fscy100)")
    if shake:  # wobble after landing
        a+="".join(f"\\t({190+k*60},{250+k*60},\\frz{rot+(7 if k%2==0 else -7)})" for k in range(5))
        a+=f"\\t(490,560,\\frz{rot})"
    a+=f"\\t({max(dur-130,200)},{dur},\\fscx0\\fscy0\\alpha&HFF&)}}"
    ev.append(f"Dialogue: {layer},{ts(t0)},{ts(t1)},{style},,0,0,0,,{a}{txt}")
def phrase(items,t_end,x,y0,gap=1.25,tilt=None):
    """items: (time,text,style,size,shake). stacked downward from y0"""
    y=y0; prev=None
    for i,(t,txt,st,sz,sh) in enumerate(items):
        if prev: y+=int((prev+sz)/2*1.05)+44
        r = tilt[i%len(tilt)] if tilt else random.choice([-6,-4,4,6])
        word(t,t_end,txt,x,y,st,sz,r,sh); prev=sz
# 1. intro (group shot, faces in the upper-middle) -> text in lower third
phrase([(0.17,"СЕГОДНЯ","W",96,0),(0.45,"ВЕЧЕР","Y",110,0),(0.97,"ПЯТНИЦА!","P",120,0)],1.52,540,1330,tilt=[-5,4,-3])
phrase([(1.55,"И НАМ СТАЛО","W",92,0),(1.99,"СКУЧНО...","K",150,1)],2.56,540,1380,tilt=[3,-6])
phrase([(2.59,"ПОЭТОМУ МЫ","W",92,0),(3.03,"ПРИШЛИ","Y",120,0)],3.26,540,1380,tilt=[-4,5])
phrase([(3.27,"В GOOD NIGHT","P",110,0),(3.83,"SHOW!","K",190,1)],4.18,540,1330,tilt=[-5,4])
# 2. blindfolded girls on the floor -> text up top
phrase([(8.54,"КАКИЕ","W",100,0),(8.70,"СЕРЬЁЗНЫЕ","Y",120,0),(9.26,"ДВИЖЕНИЯ!","P",120,1)],10.32,540,420,tilt=[-6,3,-4])
phrase([(10.36,"ПОДНИМАЙ","W",110,0),(10.76,"НОГУ!","K",170,1)],11.0,540,480,tilt=[5,-6])
# 3. charades: faces high -> text low
word(12.57,13.19,"ТАКСИ?!","Y",(540-0),1450,None) if False else None
phrase([(12.57,"ТАКСИ?!","Y",150,1)],13.19,540,1480,tilt=[-7])
phrase([(13.21,"АБСОЛЮТНО","W",110,0),(13.81,"ВЕРНО!","K",170,1)],14.35,540,1420,tilt=[4,-5])
# 4. "Он наш!"  faces mid -> text top
phrase([(16.48,"ОН НАШ!","Y",150,1)],17.32,540,470,tilt=[-6])
phrase([(17.34,"МЫ","W",110,0),(17.60,"ЗАБРАЛИ!","P",130,0)],18.36,540,430,tilt=[5,-4])
phrase([(18.38,"ОН","W",120,0),(18.55,"НАШ!!!","K",200,1)],19.13,540,400,tilt=[-5,6])
# 5. scattered "НЯ!" stickers
for t,(x,y),st in zip([19.55,19.99,20.33,20.60,20.80,20.98,21.12],
                      [(250,420),(800,560),(330,1500),(780,1320),(540,300),(230,960),(850,1000)],
                      ["Y","P","K","W","Y","P","K"]):
    word(t,21.24,"НЯ!",x,y,st,random.choice([110,130,150]),random.randint(-18,18),True)
# 6. host voice over the ending
phrase([(25.78,"ВСЁ!","K",190,1)],26.20,540,1400,tilt=[-6])
phrase([(26.20,"ЭТО БЫЛО","W",110,0),(26.76,"КЛАССНО!","Y",140,1)],27.20,540,1350,tilt=[4,-5])
phrase([(27.20,"ОТЛИЧНО,","W",110,0),(27.96,"ДРУЗЬЯ!","P",140,1)],28.50,540,470,tilt=[-4,5])
# 7. finale stamp
phrase([(28.55,"ВСЁ БУДЕТ","W",120,0),(28.80,"ХОРОШО!","Y",170,1)],30.0,540,1380,tilt=[-4,3])
ev=[e for e in ev if e]
open(S+"/tools/subs.ass","w").write(hdr+"\n".join(ev)+"\n")
print(len(ev),"events")
