# Detect faces (YuNet) every 5th frame; output boxes in 1080x1920 coords with timestamps
import cv2, sys, json
vid, out = sys.argv[1], sys.argv[2]
cap=cv2.VideoCapture(vid); fps=cap.get(cv2.CAP_PROP_FPS) or 30
W=int(cap.get(3)); H=int(cap.get(4)); k=1080/W
det=cv2.FaceDetectorYN.create("/home/user/venvs/models/yunet.onnx","",(540,960),0.5,0.3,5000)
res=[]; i=0
while True:
    ok,fr=cap.read()
    if not ok: break
    if i%5==0:
        small=cv2.resize(fr,(540,960)); s=1080/540
        _,f=det.detect(small)
        boxes=[] if f is None else [[round(float(x)*s),round(float(y)*s),round(float(w)*s),round(float(h)*s),round(float(c),2)] for x,y,w,h,*_,c in f]
        res.append([round(i/fps,3),boxes])
    i+=1
json.dump(res,open(out,"w")); print("faces:",sum(len(b) for _,b in res),"in",len(res),"samples")
