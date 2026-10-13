# 1080x1920 hikâyeyi %75 küçültüp 1080x1440 gönderiye genişletir:
# yanlara zemin, kırmızı alan ve yaylar devam ettirilir.
import sys
from PIL import Image, ImageDraw
import numpy as np
src, out = sys.argv[1], sys.argv[2]
import os
K=float(os.environ.get('KAYMA','0'))
S=0.75; OX=135; W,H=1080,1440
st=Image.open(src).convert("RGB").resize((810,1440),Image.LANCZOS)
s=np.asarray(st).astype(float)
c=np.zeros((H,W,3)); c[:,OX:OX+810]=s
slope=90/1079
def kenar_sol(x): return (1370-K)*S+slope*(OX-x)
def kenar_sag(x): return (1280-K)*S-slope*(x-(OX+810))
# beyaz zemin: kenar sütunundaki yay piksellerini satırlar arası doldur
def zemin_sutun(col):
  v=col.copy(); kirli=(v[:,0]-v[:,1]>12)
  iyi=np.nonzero(~kirli)[0]
  for ch in range(3): v[:,ch]=np.interp(np.arange(H),iyi,v[iyi,ch])
  return v
solB=zemin_sutun(s[:,0]); sagB=zemin_sutun(s[:,809])
for x in range(0,OX):
  e=kenar_sol(x)
  for y in range(H):
    t=np.clip(y-e+0.5,0,1)
    kir=s[max(y,int((1370-K)*S)+2),0]
    c[y,x]=solB[min(y,int((1370-K)*S)-2)]*(1-t)+kir*t
for x in range(OX+810,W):
  e=kenar_sag(x)
  for y in range(H):
    t=np.clip(y-e+0.5,0,1)
    kir=s[max(y,int((1280-K)*S)+2),809]
    c[y,x]=sagB[min(y,int((1280-K)*S)-2)]*(1-t)+kir*t
img=Image.fromarray(np.clip(c,0,255).astype("uint8"))
# yaylar: hikâyedeki uç noktalardan aynı eğrilik ve incelme ile dışa uzatılır
import math
def cember(p1,p2,p3):
  (x1,y1),(x2,y2),(x3,y3)=p1,p2,p3
  d=2*(x1*(y2-y3)+x2*(y3-y1)+x3*(y1-y2))
  ux=((x1*x1+y1*y1)*(y2-y3)+(x2*x2+y2*y2)*(y3-y1)+(x3*x3+y3*y3)*(y1-y2))/d
  uy=((x1*x1+y1*y1)*(x3-x2)+(x2*x2+y2*y2)*(x1-x3)+(x3*x3+y3*y3)*(x2-x1))/d
  return ux,uy,math.hypot(x1-ux,y1-uy)
K=4; lay=Image.new("RGBA",(W*K,H*K),(0,0,0,0)); d=ImageDraw.Draw(lay)
yaylar=[ # (x=0,20,60'taki merkez çizgisi y), uçtaki kalınlık, incelme/px, renk
  ((804,788.5,759),2.3,0.0045,(248,175,178,255)),
  ((873.5,853.5,818),7.1,0.025,(238,50,57,255)),
]
for (y0,y20,y60),w0,inc,col in yaylar:
  for yon in (1,-1):
    X=lambda x: x if yon==1 else 1079-x
    cx,cy,r=cember((X(0),y0),(X(20),y20),(X(60),y60))
    ust=[];alt=[]
    for k in range(0,241):
      x=-k  # hikâye koordinatı, dışa doğru
      xs=X(x)
      dy=math.sqrt(max(r*r-(xs-cx)**2,0)); y=cy-dy
      nx,ny=(xs-cx)/r,(y-cy)/r
      w=max(w0-inc*k,0.6)/2
      f=lambda px,py:((OX+px*S)*K,(py*S)*K)
      ust.append(f(xs+nx*w,y+ny*w)); alt.append(f(xs-nx*w,y-ny*w))
    d.polygon(ust+alt[::-1],fill=col)
lay=lay.resize((W,H),Image.LANCZOS)
m=Image.new("L",(W,H),0); ImageDraw.Draw(m).rectangle([0,0,OX+1,1000],fill=255); ImageDraw.Draw(m).rectangle([OX+808,0,W,1000],fill=255)
la=np.asarray(lay).astype(float); mm=np.asarray(m).astype(float)/255
al=la[...,3:]/255*mm[...,None]
base=np.asarray(img).astype(float)
res=base*(1-al)+la[...,:3]*al
Image.fromarray(np.clip(res,0,255).astype("uint8")).save(out)
