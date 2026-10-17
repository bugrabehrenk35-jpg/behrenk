# Yüksek çözünürlüklü sürüm (2250x3200): Real-ESRGAN + klasik büyütme harmanı,
# CHP rozeti silinir, kubbeli ve kalınlıklı Yeni Parti rozeti yerleştirilir.
# Kullanım: python3 rozet2.py sr_x4.png
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as nd

K = 2
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

# 3) rozet: kubbeli beyaz emaye, gümüş kenar, logo, parlama
S = 800
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
nx, ny = (xx - S / 2) / (S / 2), (yy - S / 2) / (S / 2)
r = np.hypot(nx, ny)
RIM = 0.92
ic = r < RIM
nz = np.sqrt(np.clip(1 - (r / 1.6) ** 2, 0, 1))          # hafif kubbe
lx, ly, lz_ = -0.45, -0.55, 0.70                          # ışık: üst-sol-önden
dif = np.clip((nx / 1.6) * lx + (ny / 1.6) * ly + nz * lz_, 0, 1)
emaye = (np.array([226, 228, 234], np.float32)[None, None] * (0.80 + 0.26 * dif)[..., None])
# gümüş kenar: üst-sol parlak, alt-sağ koyu, ince bevel
aci = np.cos(np.arctan2(ny, nx) + 2.36)
gumus = (150 + 75 * aci)[..., None] * np.array([1, 1.01, 1.04])[None, None]
renk = np.where(ic[..., None], emaye, gumus)
alfa = np.clip((1 - r) * S / 2, 0, 1)                   # kenar yumuşatma
roz = np.dstack([renk, alfa * 255])
# emaye ile kenar arasında ince koyu çizgi
cizgi = np.exp(-((r - RIM) * S / 2 / 2.2) ** 2)
roz[..., :3] *= (1 - 0.35 * cizgi)[..., None]
roz = Image.fromarray(roz.clip(0, 255).astype(np.uint8), 'RGBA')

logo = Image.open('yp-logo-beyaz.png').convert('RGBA')
la = np.asarray(logo)[..., 3].astype(np.float32)
lr = np.zeros((*la.shape, 3), np.float32)
lr[:700] = (205, 28, 40); lr[700:] = (46, 48, 56)
lg = Image.fromarray(np.dstack([lr, la]).astype(np.uint8), 'RGBA')
lw = int(S * 0.70); lh = round(lg.height * lw / lg.width)
lg = lg.resize((lw, lh), Image.LANCZOS)
roz.alpha_composite(lg, ((S - lw) // 2, (S - lh) // 2 + 8))
# logo baskısına da kubbe ışığını uygula
ra = np.asarray(roz).astype(np.float32)
ra[..., :3] *= np.where(ic, 0.90 + 0.14 * dif, 1)[..., None]
# yumuşak parlama + kenarda ince parlak yay
pr = Image.new('L', (S, S), 0)
ImageDraw.Draw(pr).ellipse([S * .16, S * .10, S * .58, S * .36], fill=85)
pr = np.asarray(pr.filter(ImageFilter.GaussianBlur(S * .045))).astype(np.float32) / 255
yay = np.exp(-((r - 0.86) * S / 2 / 4) ** 2) * np.clip(aci, 0, 1) * 0.55
isik = np.clip(pr * ic + yay, 0, 1)
ra[..., :3] = ra[..., :3] * (1 - isik[..., None]) + 255 * isik[..., None]
roz = Image.fromarray(ra.clip(0, 255).astype(np.uint8), 'RGBA')

# 4) yerleştir: boyut, perspektif, kalınlık, iki katmanlı gölge
CAP = 46 * K
cx, cy = 788 * K, 851 * K
k = roz.resize((CAP, round(CAP * 0.95)), Image.LANCZOS).rotate(-7, resample=Image.BICUBIC, expand=True)
kw, kh = k.size
px, py = cx - kw // 2, cy - kh // 2
ka = np.zeros((H, W), np.float32)
ka[py:py + kh, px:px + kw] = np.asarray(k.split()[3]).astype(np.float32) / 255
def kaydir(a, dx, dy): return nd.shift(a, (dy, dx), order=1)
yan = np.clip(kaydir(ka, 2.2, 3.0) - ka, 0, 1)                      # rozetin kenar kalınlığı
genis = nd.gaussian_filter(kaydir(ka, 6, 9), 9)
siki = nd.gaussian_filter(kaydir(ka, 2.5, 3.5), 2.5)
A *= (1 - 0.30 * genis - 0.55 * siki * (1 - ka))[..., None]
A = A * (1 - yan[..., None]) + np.array([92, 93, 98], np.float32) * yan[..., None]
out = Image.fromarray(A.clip(0, 255).astype(np.uint8)).convert('RGBA')
out.alpha_composite(k.filter(ImageFilter.GaussianBlur(0.7)), (px, py))
o = np.asarray(out.convert('RGB')).astype(np.float32)
o += nd.gaussian_filter(rng.normal(0, 1.8, (H, W)), 0.6)[..., None] * 1.4 * ka[..., None]
Image.fromarray(o.clip(0, 255).astype(np.uint8)).save('yeni-parti-rozetli-hd.jpg', quality=97, subsampling=0)
print('ok', W, H)
