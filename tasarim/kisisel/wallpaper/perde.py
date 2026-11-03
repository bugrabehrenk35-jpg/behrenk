# Perde zeminli duvar kağıdı (Talat Yalaz görselindeki teal perde tonu), krem imza.
import numpy as np
from PIL import Image, ImageFilter
K=2; W,H=1206*K,2622*K
x=np.arange(W,dtype=np.float32)/K; y=np.arange(H,dtype=np.float32)[:,None]/H
# düzensiz kıvrımlar: farklı periyotlarda yumuşak sinüsler, hafif dalgalanma
rng=np.random.default_rng(4); f=np.zeros(W,np.float32)
for per,amp in [(150,1.0),(97,.55),(233,.7),(61,.25)]:
    f+=amp*np.sin(2*np.pi*x/per+rng.uniform(0,6))
f=(f-f.min())/(f.max()-f.min())            # 0..1
kiv=(f**1.6)[None,:]                         # tepe ışıkları dar, gölgeler geniş
ust=np.array([92,113,112]); orta=np.array([66,82,81]); alt=np.array([8,9,9])
def renk(t):
    t=np.clip(t,0,1); c1=np.clip(t/.55,0,1)[...,None]; c2=np.clip((t-.55)/.42,0,1)[...,None]
    return ust*(1-c1)+orta*c1*(1-c2)+alt*c2
zemin=renk(y[:,0])[:,None,:].astype(np.float32)          # H,1,3
img=zemin*(0.62+0.62*kiv[...,None])                       # H,W,3
# ortada sıcak hafif ışık
xx=(np.arange(W)/W-.5)[None,:]; yy=y-.6
img+=np.exp(-(xx**2/.12+yy**2/.03))[...,None]*np.array([20,14,10])
# vinyet
d=np.hypot(xx*2,(y-.5)*2); img*=(1-0.5*np.clip(d-0.6,0,1))[...,None]
img+=rng.normal(0,4.5,(H,W,1))
bg=Image.fromarray(img.clip(0,255).astype(np.uint8)).convert('RGBA')
im=Image.open('imza-krem.png'); iw=int(W*.80); im=im.resize((iw,int(im.height*iw/im.width)),Image.LANCZOS)
px,py=(W-iw)//2,int(H*.635)-im.height//2
m=Image.new('L',bg.size,0); m.paste(im.split()[3],(px,py)); sh=Image.new('RGBA',bg.size,(0,0,0,0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(36)).point(lambda v:int(v*.75)))
bg.alpha_composite(sh); bg.alpha_composite(im,(px,py))
bg.convert('RGB').resize((1206,2622),Image.LANCZOS).save('wallpaper-iphone17pro-perde.png',optimize=True)
