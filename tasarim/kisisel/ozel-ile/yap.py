import numpy as np,cv2
from PIL import Image,ImageFilter
K=3; W,H=1080*K,1350*K
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
# zemin: derin kırmızı, sol üstten ışık
d=np.hypot((xx-W*.42)/(W*.75),(yy-H*.30)/(H*.62))
t=np.clip(d,0,1)[...,None]
c1=np.array([196,22,32],np.float32); c2=np.array([92,9,15],np.float32); c3=np.array([28,5,8],np.float32)
bg=c1*(1-t)+c2*t
v=np.clip((yy/H-.55)/.45,0,1)[...,None]**1.4; bg=bg*(1-v)+c3*v
# çapraz ince ışık bantları
s=np.sin((xx*.55-yy)/(W*.05))*.5+.5; bg+= (s**14)[...,None]*np.array([22,4,6],np.float32)*(1-v)
img=Image.fromarray(bg.clip(0,255).astype(np.uint8)).convert('RGBA')
def yerlestir(f,sc,x,y,blur=0,dark=1.0):
    im=Image.open(f).convert('RGBA'); im=im.resize((int(im.width*sc*K),int(im.height*sc*K)),Image.LANCZOS)
    if blur: im=im.filter(ImageFilter.GaussianBlur(blur))
    if dark!=1.0:
        a=np.asarray(im).astype(np.float32); a[...,:3]*=dark; im=Image.fromarray(a.clip(0,255).astype(np.uint8))
    return im,(int(x*K),int(y*K))
b,bp=yerlestir('bugra-kesik.png',0.32,438,262,blur=0.9,dark=0.93)
ba=np.asarray(b).astype(np.float32); hh=ba.shape[0]; f=np.clip((np.arange(hh)-hh*.80)/(hh*.18),0,1)[:,None]; ba[...,3]*=1-f; b=Image.fromarray(ba.astype(np.uint8))
o,op=yerlestir('ozel-kesik.png',0.52,-175,228)
oa=np.asarray(o).astype(np.float32); oa[...,3]=oa[...,3]; o=Image.fromarray(oa.astype(np.uint8))
# arka kişinin arkasına yumuşak gölge
for im,pos,op_,r in [(b,bp,.45,60)]:
    sh=Image.new('RGBA',img.size,(0,0,0,0)); m=Image.new('L',img.size,0); m.paste(im.split()[3],pos)
    sh.putalpha(m.filter(ImageFilter.GaussianBlur(r)).point(lambda q:int(q*op_))); img.alpha_composite(sh)
img.alpha_composite(b,bp)
# özel'in buğra üzerine düşen gölgesi
m=Image.new('L',img.size,0); m.paste(o.split()[3],(op[0]+40*K,op[1]+10*K))
sh=Image.new('RGBA',img.size,(0,0,0,0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(45*K)).point(lambda q:int(q*.55)))
bm=Image.new('L',img.size,0); bm.paste(b.split()[3],bp)
sh.putalpha(Image.fromarray(np.minimum(np.asarray(sh.split()[3]),np.asarray(bm))))
img.alpha_composite(sh)
img.alpha_composite(o,op)
# alt koyulaşma
a=np.asarray(img).astype(np.float32)
g=np.clip((yy/H-.80)/.20,0,1)**1.3; a[...,:3]=a[...,:3]*(1-.75*g[...,None])+np.array([20,4,6])*.75*g[...,None]
# logo
img=Image.fromarray(a.clip(0,255).astype(np.uint8))
lg=Image.open('yp-logo-beyaz.png').convert('RGBA'); lg=lg.crop(lg.getbbox()); lw=int(250*K); lg=lg.resize((lw,int(lg.height*lw/lg.width)),Image.LANCZOS)
img.alpha_composite(lg,(int(72*K),int(72*K)))
# gren
rng=np.random.default_rng(3); arr=np.asarray(img.convert('RGB')).astype(np.float32)+rng.normal(0,3.2,(H,W,1))
out=Image.fromarray(arr.clip(0,255).astype(np.uint8))
out.save('ozel-bugra-3240x4050.jpg',quality=96,subsampling=0); out.resize((1080,1350),Image.LANCZOS).save('ozel-bugra-1080x1350.png')
