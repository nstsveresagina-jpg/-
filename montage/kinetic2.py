# Kinetic sticker text, auto-placed so that it never covers a detected face.
import sys, json, random
random.seed(7)
faces=json.load(open(sys.argv[1])); OUT=sys.argv[2]
PAD=60  # extra space around every face (hair, forehead, rotation)
def face_boxes(t0,t1):
    bx=[]
    for t,bs in faces:
        if t0-0.15<=t<=t1+0.15:
            for x,y,w,h,c in bs:
                # enlarge: faces detector box is tight; include hair above/below chin
                bx.append((x-PAD, y-PAD-0.35*h, x+w+PAD, y+h+PAD+0.15*h))
    return bx
def text_w(txt,sz): return len(txt)*sz*0.66+2*18+30
def hit(r,bx): return any(not(r[2]<b[0] or r[0]>b[2] or r[3]<b[1] or r[1]>b[3]) for b in bx)
def layout(items,y0,x):
    rects=[];y=y0;prev=None;pos=[]
    for t,txt,st,sz,sh in items:
        if prev: y+=int((prev+sz)/2*1.05)+44
        w=text_w(txt,sz); hh=sz*1.05+36
        rects.append((x-w/2,y-hh/2,x+w/2,y+hh/2)); pos.append((x,y)); prev=sz
    return rects,pos
def place(items,t0,t1,pref):
    bx=face_boxes(t0,t1); best=None
    for scale in (1.0,0.85,0.72):
        its=[(t,tx,st,int(sz*scale),sh) for t,tx,st,sz,sh in items]
        cands=[]
        for x in (540,420,660,330,750):
            for y0 in range(170,1800,20):
                rects,pos=layout(its,y0,x)
                if rects[0][1]<110 or rects[-1][3]>1840 or min(r[0] for r in rects)<20 or max(r[2] for r in rects)>1060: continue
                if any(hit(r,bx) for r in rects): continue
                cy=(rects[0][1]+rects[-1][3])/2
                cands.append((abs(cy-pref)+abs(x-540)*0.8,its,pos))
        if cands:
            return min(cands,key=lambda c:c[0])[1:]
    print("WARN no free spot",items[0][1],t0)
    its=[(t,tx,st,int(sz*0.72),sh) for t,tx,st,sz,sh in items]
    return its,layout(its,1700-len(its)*120,540)[1]
def ts(t): return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
ev=[]
def word(t0,t1,txt,x,y,style,size,rot,shake):
    dur=int((t1-t0)*1000)
    a=(f"{{\\pos({x},{y})\\fs{size}\\frz{rot}\\fscx0\\fscy0\\t(0,90,\\fscx128\\fscy128)\\t(90,190,\\fscx100\\fscy100)")
    if shake:
        a+="".join(f"\\t({190+k*60},{250+k*60},\\frz{rot+(7 if k%2==0 else -7)})" for k in range(5))+f"\\t(490,560,\\frz{rot})"
    a+=f"\\t({max(dur-130,200)},{dur},\\fscx0\\fscy0\\alpha&HFF&)}}"
    ev.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},{style},,0,0,0,,{a}{txt}")
def phrase(items,t_end,pref,tilt):
    its,pos=place(items,items[0][0],t_end,pref)
    for i,((t,txt,st,sz,sh),(x,y)) in enumerate(zip(its,pos)):
        word(t,t_end,txt,int(x),int(y),st,sz,tilt[i%len(tilt)],sh)
LOW,HIGH=1400,450
# --- phrases: (time, text, style, size, shake); all words are spoken in that same shot
phrase([(0.17,"СЕГОДНЯ","W",96,0),(0.45,"ВЕЧЕР","Y",110,0),(0.97,"ПЯТНИЦА!","P",120,0)],1.52,LOW,[-5,4,-3])
phrase([(1.55,"И НАМ СТАЛО","W",92,0),(1.99,"СКУЧНО...","K",150,1)],2.56,LOW,[3,-6])
phrase([(2.59,"ПОЭТОМУ МЫ","W",92,0),(3.03,"ПРИШЛИ","Y",120,0)],3.26,LOW,[-4,5])
phrase([(3.27,"В GOOD NIGHT","P",110,0),(3.83,"SHOW!","K",190,1)],4.18,LOW,[-5,4])
phrase([(5.25,"ЛЯЖЬ","W",120,0),(5.55,"НА ПОЛ!","Y",150,1)],6.20,HIGH,[-6,4])
phrase([(6.22,"ПАДАЙ!","K",190,1)],7.31,HIGH,[5])
phrase([(10.01,"КАКИЕ","W",100,0),(10.17,"СЕРЬЁЗНЫЕ","Y",120,0),(10.73,"ДВИЖЕНИЯ!","P",120,1)],11.80,HIGH,[-6,3,-4])
phrase([(11.83,"ПОДНИМАЙ","W",110,0),(12.23,"НОГУ!","K",170,1)],12.58,HIGH,[5,-6])
phrase([(15.16,"ВОЛНА!","P",170,1)],15.95,HIGH,[-6])
phrase([(16.45,"ТАКСИ?!","Y",150,1)],17.08,LOW,[-7])
phrase([(17.09,"АБСОЛЮТНО","W",110,0),(17.69,"ВЕРНО!","K",170,1)],18.06,LOW,[4,-5])
phrase([(19.35,"ОПУСТИ,","W",100,0),(19.61,"ПОЖАЛУЙСТА,","Y",100,0),(20.17,"ПЯТОЧКИ","P",120,0),(20.67,"ВНИЗ!","K",160,1)],21.24,HIGH,[-5,4,-4,6])
phrase([(21.24,"ОН НАШ!","Y",150,1)],22.08,HIGH,[-6])
phrase([(22.10,"МЫ","W",110,0),(22.36,"ЗАБРАЛИ!","P",130,0)],23.12,HIGH,[5,-4])
phrase([(23.14,"ОН","W",120,0),(23.31,"НАШ!!!","K",200,1)],23.89,HIGH,[-5,6])
phrase([(27.08,"ТАИЛАНД!","Y",160,1)],28.65,HIGH,[-6])
# scattered НЯ! (each sticker avoids faces too)
for t,st in zip([30.16,30.50,30.92,31.12,31.32,31.50,31.66],["Y","P","K","W","Y","P","K"]):
    sz=random.choice([110,130,150]); bx=face_boxes(t,31.83)
    for _ in range(400):
        x=random.randint(170,910); y=random.randint(250,1700); w=text_w("НЯ!",sz)
        if not hit((x-w/2,y-sz*0.6,x+w/2,y+sz*0.6),bx): break
    word(t,31.83,"НЯ!",x,y,st,sz,random.randint(-18,18),True)
phrase([(33.4,"ВСЁ БУДЕТ","W",120,0),(33.7,"ХОРОШО!","Y",170,1)],37.13,LOW,[-4,3])
hdr=open("/tmp/claude-0/-home-user--/c1d483ab-d94d-56fe-b8d8-24fe5041141f/scratchpad/tools/subs.ass").read().split("[Events]")[0]
open(OUT,"w").write(hdr+"[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"+"\n".join(ev)+"\n")
print(len(ev),"events")
