# Kişiyi %20 büyütüp kırmızı kenarın arkasına yerleştirir: zemin.png -> zemin-buyuk.png
from PIL import Image, ImageFilter
import numpy as np
Z=Image.open("zemin.png").convert("RGB"); W,H=Z.size
cut=Image.open("kisi-kesik-buyuk.png").convert("RGBA"); OY=560
edge=lambda x:1370-(90/1079)*x
a=np.asarray(cut.split()[3]).astype(float)/255
yy,xx=np.mgrid[0:a.shape[0],0:a.shape[1]]
a=a*np.clip(edge(xx)-(yy+OY)-0.5,0,1)
z=np.asarray(Z).astype(float)
m=np.asarray(Image.fromarray((a>0.04).astype("uint8")*255).filter(ImageFilter.MaxFilter(9)))>0
for y in range(m.shape[0]):
  row=m[y]
  if not row.any(): continue
  Y=y+OY; xs=np.nonzero(~row)[0]
  for ch in range(3):
    z[Y,:,ch]=np.where(row,np.interp(np.arange(W),xs,z[Y,xs,ch]),z[Y,:,ch])
s=1.2; ax_old,ay_old=540,655; ax_new,ay_new=428,602
big=cut.resize((int(cut.width*s),int(cut.height*s)),Image.LANCZOS)
px=int(round(ax_new-s*ax_old)); py=int(round(ay_new-s*(ay_old-OY)))
lay=Image.new("RGBA",(W,H),(0,0,0,0)); lay.paste(big,(px,py))
la=np.asarray(lay).astype(float)
YY,XX=np.mgrid[0:H,0:W]
al=la[...,3]/255*np.clip(edge(XX)-YY-0.5,0,1)
out=z*(1-al[...,None])+la[...,:3]*al[...,None]
Image.fromarray(out.clip(0,255).astype("uint8")).save("zemin-buyuk.png")
