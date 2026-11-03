# iPhone 17 Pro duvar kağıdı: 1206x2622 (2x üretilip küçültülür). Koyu zemin, ortada imza.
import numpy as np
from PIL import Image, ImageFilter
K=2; W,H=1206*K,2622*K
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
# zemin: neredeyse siyah, alttan derin kırmızı ışıma, üstte soğuk koyu
base=np.zeros((H,W,3),np.float32)+np.array([11,10,12],np.float32)
g=np.exp(-(((xx-W*.5)/(W*.62))**2+((yy-H*.66)/(H*.30))**2))
base+=g[...,None]*np.array([42,4,8],np.float32)
g2=np.exp(-(((xx-W*.5)/(W*.35))**2+((yy-H*.64)/(H*.10))**2))
base+=g2[...,None]*np.array([14,2,4],np.float32)
# ince çapraz ışık süzmesi
s=np.sin((xx*0.6+yy)/(W*0.11))*0.5+0.5
base+=(s**8)[...,None]*np.array([5,4,4],np.float32)
# vinyet
d=np.hypot((xx-W/2)/(W/2),(yy-H/2)/(H/2)); base*=(1-0.45*np.clip(d-0.55,0,1))[...,None]
img=Image.fromarray(base.clip(0,255).astype(np.uint8)).convert('RGBA')
# imza: renkli sürüm, koyu gri kısımlar açık renge
im=Image.open('../imza-orijinal.png').convert('RGBA'); a=np.asarray(im).astype(np.float32)
r,gc,b,al=a[...,0],a[...,1],a[...,2],a[...,3]
koyu=(r-gc<40)&(np.maximum(np.maximum(r,gc),b)<150)
a[koyu,0:3]=[232,226,220]
im=Image.fromarray(a.clip(0,255).astype(np.uint8),'RGBA')
bb=im.getbbox(); im=im.crop(bb)
iw=int(W*0.80); im=im.resize((iw,int(im.height*iw/im.width)),Image.LANCZOS)
x=(W-iw)//2; y=int(H*0.635)-im.height//2
# imza arkasında yumuşak gölge
sh=Image.new('RGBA',img.size,(0,0,0,0)); m=Image.new('L',img.size,0); m.paste(im.split()[3],(x,y)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(40)).point(lambda v:int(v*.7)))
img.alpha_composite(sh); img.alpha_composite(im,(x,y))
# gren
rng=np.random.default_rng(7); n=rng.normal(0,5,(H,W,1)).astype(np.float32)
arr=np.asarray(img.convert('RGB')).astype(np.float32)+n
out=Image.fromarray(arr.clip(0,255).astype(np.uint8)).resize((1206,2622),Image.LANCZOS)
out.save('wallpaper-iphone17pro.png',optimize=True); print(out.size)
