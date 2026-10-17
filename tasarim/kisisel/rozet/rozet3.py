# Yüksek çözünürlüklü sürüm (2250x3200): Real-ESRGAN + klasik büyütme harmanı,
# CHP rozeti silinir, Dilaver Demir fotoğrafındaki gerçek rozet kesilip büyütülerek takılır.
# Kullanım: python3 rozet3.py sr_x4.png dilaver-rozet-kaynak.png
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as nd

K = 2
RX, RY = -0.3, -0.3
HEDEF = (232, 233, 238)
ORAN = 0.86
ACI = -4
CIKTI = 'yeni-parti-rozetli-hd.jpg'
org = Image.open('orijinal.jpg').convert('RGB')
W0, H0 = org.size
W, H = W0 * K, H0 * K

# 1) taban: ESRGAN'ı 2 kata indir, klasik büyütmeyle harmanla, ince gren ekle
esr = Image.open(sys.argv[1]).convert('RGB').resize((W, H), Image.LANCZOS)
lz = org.resize((W, H), Image.LANCZOS)
E = np.asarray(esr).astype(np.float32); L = np.asarray(lz).astype(np.float32)
detay = E - nd.gaussian_filter(E, (1.6, 1.6, 0))          # sadece ince detay (kirpik, kaş, kenar)
A = L - 0.55 * (L - nd.gaussian_filter(L, (1.6, 1.6, 0))) + 0.75 * detay
rng = np.random.default_rng(11)
A += nd.gaussian_filter(rng.normal(0, 1.6, (H, W)), 0.6)[..., None] * 1.4

# 2) CHP rozetini sil
x0, y0, x1, y1 = 754 * K, 819 * K, 822 * K, 882 * K
mask = np.zeros((H, W), bool); mask[y0:y1, x0:x1] = True
pad = 20
sl = (slice(y0 - pad, y1 + pad), slice(x0 - pad, x1 + pad))
blk = A[sl].copy(); mk = mask[sl]
_w = (~mk).astype(np.float32)
_n = np.stack([nd.gaussian_filter(blk[..., c] * _w, 25) for c in range(3)], -1)
blk[mk] = (_n / np.maximum(nd.gaussian_filter(_w, 25), 1e-4)[..., None])[mk]   # çevre renginden başlat
for _ in range(1500):
    blur = nd.uniform_filter(blk, (3, 3, 1))
    blk[mk] = blur[mk]
DX = 72 * K
src = A[y0 - pad:y1 + pad, x0 - DX - pad:x1 - DX + pad]
doku = src - nd.gaussian_filter(src, (10, 10, 0))
yama = blk + doku
yum = np.clip(nd.gaussian_filter(mask.astype(np.float32), 5)[sl] * 1.6, 0, 1)[..., None]
A[sl] = A[sl] * (1 - yum) + yama * yum

# 3) gerçek rozet: Dilaver Demir'in fotoğrafındaki rozeti kes
kay = np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(np.float32) / 255
CX, CY = 121.7, 102.3                         # rozet merkezi (kaynak kesitte)
bx0, by0 = int(CX) - 60, int(CY) - 50
kes = kay[by0:by0 + 100, bx0:bx0 + 120]
# kaynak rozet hedefle neredeyse aynı boyutta: gerçek pikselleri klasik büyütmeyle kullan
up = np.asarray(Image.fromarray((kes * 255).astype(np.uint8)).resize((480, 400), Image.LANCZOS)).astype(np.float32)
uh, uw, _ = up.shape
yy, xx = np.mgrid[0:uh, 0:uw].astype(np.float32)
th = np.deg2rad(5.9)
dx, dy = xx - (CX - bx0) * 4, yy - (CY - by0) * 4
u = dx * np.cos(th) + dy * np.sin(th); v = -dx * np.sin(th) + dy * np.cos(th)
A_, B_ = (41 + RX) * 4, (29 + RY) * 4
d = np.sqrt((u / A_) ** 2 + (v / B_) ** 2)
alfa = np.clip((1 - d) * min(A_, B_) / 5 + 0.5, 0, 1)        # ~1 px yumuşak kenar
# renk: emaye beyazını bu fotoğrafın ışığına eşitle
Lu = up.mean(2); sat = up.max(2) - up.min(2)
beyaz = (alfa > 0.9) & (Lu > np.percentile(Lu[alfa > 0.9], 70)) & (sat < 40)
kazanc = np.array(HEDEF, np.float32) / up[beyaz].mean(0)
up = up * kazanc
# baskı kırmızısını parti kırmızısına yaklaştır (pembeleşmiş tonu topla)
kir = np.clip((up[..., 0] - up[..., 1] - 25) / 60, 0, 1)[..., None] * (alfa > 0.5)[..., None]
lum = up.mean(2, keepdims=True)
up = up * (1 - 0.55 * kir) + (np.array([200, 30, 42], np.float32) * (lum / 92)) * 0.55 * kir
roz = Image.fromarray(np.dstack([up, alfa * 255]).clip(0, 255).astype(np.uint8), 'RGBA')
# açıyı düzelt, yakanın açısına göre oranla, sonra hedef açıya döndür
roz = roz.rotate(np.rad2deg(th), resample=Image.BICUBIC, center=((CX - bx0) * 4, (CY - by0) * 4))
roz = roz.crop(roz.split()[3].point(lambda p: 255 if p > 8 else 0).getbbox())

# 4) yerleştir
GEN = 47 * K
k = roz.resize((GEN, round(GEN * ORAN)), Image.LANCZOS).rotate(ACI, resample=Image.BICUBIC, expand=True)
k = k.filter(ImageFilter.GaussianBlur(0.4))
cx, cy = 788 * K, 851 * K
kw, kh = k.size
px, py = cx - kw // 2, cy - kh // 2
ka = np.zeros((H, W), np.float32)
ka[py:py + kh, px:px + kw] = np.asarray(k.split()[3]).astype(np.float32) / 255
def kaydir(a, dx, dy): return nd.shift(a, (dy, dx), order=1)
siki = nd.gaussian_filter(kaydir(ka, 1.5, 2.5), 2.0)     # rozetin kumaşa değdiği yer
genis = nd.gaussian_filter(kaydir(ka, 4, 7), 7)          # yumuşak düşen gölge
cukur = nd.gaussian_filter(ka, 10) - nd.gaussian_filter(ka, 4)   # kumaşın hafif çöküşü
A *= (1 - 0.22 * genis - 0.50 * siki * (1 - ka) - 0.6 * np.clip(cukur, 0, 1) * (1 - ka))[..., None]
out = Image.fromarray(A.clip(0, 255).astype(np.uint8)).convert('RGBA')
out.alpha_composite(k, (px, py))
o = np.asarray(out.convert('RGB')).astype(np.float32)
o += nd.gaussian_filter(rng.normal(0, 1.8, (H, W)), 0.6)[..., None] * 1.3 * ka[..., None]
Image.fromarray(o.clip(0, 255).astype(np.uint8)).save(CIKTI, quality=97, subsampling=0)
print('ok', W, H, 'kazanc', kazanc.round(3), 'rozet', kw, kh)
