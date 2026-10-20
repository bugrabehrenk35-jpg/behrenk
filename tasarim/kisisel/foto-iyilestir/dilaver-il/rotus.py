# Dilaver Demir: göz altı çukurları ve diş beyazlatma. Doku (yüksek frekans) korunur, sadece düşük frekans ton düzeltilir.
import numpy as np
from PIL import Image
from scipy import ndimage as nd
from skimage.color import rgb2lab, lab2rgb
im=Image.open('orijinal.jpg'); exif=im.info.get('exif')
X0,Y0,X1,Y1=1100,590,1280,740                      # çalışma bölgesi
A=np.asarray(im.convert('RGB')).astype(np.float64)
blk=A[Y0:Y1,X0:X1]/255; lab=rgb2lab(blk); L=lab[...,0]
yy,xx=np.mgrid[Y0:Y1,X0:X1].astype(np.float64)
def elips(cx,cy,rx,ry,yum):
    d=((xx-cx)/rx)**2+((yy-cy)/ry)**2
    return nd.gaussian_filter(np.clip(1.6-d,0,1),yum)
# göz altı: alttaki yanak tonuna doğru düşük frekansı kaldır
gm=np.maximum(elips(1159,640,17,7.5,2.2),elips(1215,640,20,7.5,2.2))
low=nd.gaussian_filter(L,3)
ref=np.roll(nd.gaussian_filter(L,5),-11,axis=0)    # 11 px aşağıdaki yanak
kald=np.clip(ref-low,0,None)*0.8*gm
lab[...,0]+=kald
ab_low=nd.gaussian_filter(lab[...,1:],(3,3,0)); ab_ref=np.roll(nd.gaussian_filter(lab[...,1:],(5,5,0)),-11,axis=0)
lab[...,1:]+=(ab_ref-ab_low)*0.45*gm[...,None]
# dişler: ağız içi, açık ve düşük doygun pikseller
am=elips(1184,687.5,19,3.2,0.8)
C=np.hypot(lab[...,1],lab[...,2])
dm=am*np.clip((L-42)/10,0,1)*np.clip((30-C)/10,0,1)
dm=nd.gaussian_filter(dm,0.7)
lab[...,0]+=10*dm; lab[...,2]*=1-0.65*dm; lab[...,1]*=1-0.35*dm
out=np.clip(lab2rgb(lab),0,1)*255
B=A.copy(); B[Y0:Y1,X0:X1]=out
Image.fromarray(B.round().astype(np.uint8)).save('dilaver-iyilestirilmis.jpg',quality=97,subsampling=0,**({'exif':exif} if exif else {}))
print('ok')
