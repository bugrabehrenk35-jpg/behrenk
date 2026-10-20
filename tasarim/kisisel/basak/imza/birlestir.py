# Kullanım: python3 birlestir.py yazi-2x.png cikti.png [genislik] [alt_y]
# Ad yazısını ölçüp ortalar, TIKKIN'in üstüne hafif biner; kesiştiği yerde kırmızıda şeffaf hale açar.
import sys, numpy as np
from PIL import Image
from scipy import ndimage as nd
K=2
taban=np.asarray(Image.open(sys.argv[5] if len(sys.argv)>5 else 'taban-2x.png')).astype(np.float32)
y=Image.open(sys.argv[1]); a=np.asarray(y)[...,3]
ys,xs=np.where(a>8); y=y.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
gen=float(sys.argv[3]) if len(sys.argv)>3 else 640
alt=float(sys.argv[4]) if len(sys.argv)>4 else 318
s=gen*K/y.width
if y.height*s>(alt-8)*K: s=(alt-8)*K/y.height       # üstten taşmasın
y=y.resize((round(y.width*s),round(y.height*s)),Image.LANCZOS)
H,W=taban.shape[:2]
x0=round((960+815/2+(float(sys.argv[6]) if len(sys.argv)>6 else 0))*K-y.width/2); y0=round(alt*K-y.height)
k=np.zeros((H,W,4),np.float32); k[y0:y0+y.height,x0:x0+y.width]=np.asarray(y)
ka=k[...,3]/255
hale=np.clip(nd.gaussian_filter(nd.grey_dilation(ka,size=(13,13)),1.2)*1.2,0,1)
t=taban.copy(); t[...,3]*=(1-hale)
out=t[...,:3]*(t[...,3:]/255)*(1-ka[...,None])+k[...,:3]*ka[...,None]
al=t[...,3]/255*(1-ka)+ka
rgb=np.where(al[...,None]>0,out/np.maximum(al[...,None],1e-6),0)
Image.fromarray(np.dstack([rgb,al*255]).clip(0,255).astype(np.uint8),'RGBA').resize((W//K,H//K),Image.LANCZOS).save(sys.argv[2])
