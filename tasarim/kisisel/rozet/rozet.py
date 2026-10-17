# CHP rozetini ceket dokusuyla siler, yerine Yeni Parti rozeti yerleştirir.
# Kullanım: python3 rozet.py
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as nd

im = Image.open('orijinal.jpg').convert('RGB')
A = np.asarray(im).astype(np.float32)
H, W, _ = A.shape

# 1) CHP rozetini sil: düşük frekansı çevreden yayarak, dokuyu soldaki ceketten alarak
x0, y0, x1, y1 = 759, 824, 817, 877
mask = np.zeros((H, W), bool); mask[y0:y1, x0:x1] = True
low = nd.gaussian_filter(A, (6, 6, 0))
fill = A.copy()
for _ in range(600):                     # Laplace dolgusu (pürüzsüz ton geçişi)
    blur = nd.uniform_filter(fill, (3, 3, 1))
    fill[mask] = blur[mask]
DX = 72                                   # aynı ışıkta, rozetin solundaki ceket
src = A[y0 - 8:y1 + 8, x0 - DX - 8:x1 - DX + 8]
doku = src - nd.gaussian_filter(src, (6, 6, 0))
yama = fill[y0 - 8:y1 + 8, x0 - 8:x1 + 8] + doku
yumusak = nd.gaussian_filter(mask.astype(np.float32), 2.5)[..., None]
yumusak = np.clip(yumusak * 1.6, 0, 1)
B = A.copy()
B[y0 - 8:y1 + 8, x0 - 8:x1 + 8] = (A[y0 - 8:y1 + 8, x0 - 8:x1 + 8] * (1 - yumusak[y0 - 8:y1 + 8, x0 - 8:x1 + 8])
                                   + yama * yumusak[y0 - 8:y1 + 8, x0 - 8:x1 + 8])

# 2) Rozeti yüksek çözünürlükte çiz (beyaz emaye, gümüş kenar, parlama)
S = 640
roz = Image.new('RGBA', (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(roz)
d.ellipse([0, 0, S - 1, S - 1], fill=(176, 178, 184, 255))            # gümüş kenar
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
r = np.hypot(xx - S / 2, yy - S / 2)
ic = r < S / 2 - 26
# emaye: üst-solu biraz daha aydınlık, kenara doğru hafif koyulaşan beyaz
g = 250 - 14 * np.clip((xx + yy) / (2 * S), 0, 1) - 10 * np.clip((r / (S / 2)) ** 3, 0, 1)
emaye = np.stack([g, g, g + 1, np.where(ic, 255, 0)], -1).clip(0, 255).astype(np.uint8)
roz = Image.alpha_composite(roz, Image.fromarray(emaye))
# kenar parlaması: gümüş halkada üst-sol aydınlık, alt-sağ koyu
halka = (r >= S / 2 - 26) & (r < S / 2)
ac = np.cos(np.arctan2(yy - S / 2, xx - S / 2) + 2.36)
hk = np.zeros((S, S, 4), np.float32)
hk[..., :3] = (190 + 55 * ac)[..., None]; hk[..., 3] = np.where(halka, 255, 0)
roz = Image.alpha_composite(roz, Image.fromarray(hk.clip(0, 255).astype(np.uint8)))

logo = Image.open('yp-logo-beyaz.png').convert('RGBA')            # 1600x935, beyaz + alfa
la = np.asarray(logo)[..., 3].astype(np.float32)
renk = np.zeros((*la.shape, 3), np.float32)
renk[:700] = (214, 24, 38)                                        # YENİ kırmızı
renk[700:] = (44, 46, 54)                                         # yay + PARTİ koyu
lg = Image.fromarray(np.dstack([renk, la]).astype(np.uint8), 'RGBA')
lw = int(S * 0.74); lh = round(lg.height * lw / lg.width)
lg = lg.resize((lw, lh), Image.LANCZOS)
roz.alpha_composite(lg, ((S - lw) // 2, (S - lh) // 2 + 6))
# cam gibi parlama
pr = Image.new('L', (S, S), 0)
ImageDraw.Draw(pr).ellipse([S * .14, S * .07, S * .66, S * .40], fill=70)
pr = pr.filter(ImageFilter.GaussianBlur(S * .05))
pa = np.minimum(np.asarray(pr), np.where(ic, 255, 0)).astype(np.uint8)
roz.alpha_composite(Image.fromarray(np.dstack([np.full((S, S, 3), 255, np.uint8), pa]), 'RGBA'))

# 3) Fotoğrafa yerleştir: boyut, hafif açı, gölge, netlik ve gren
CAP = 46
cx, cy = 788, 851
k = roz.resize((CAP, CAP), Image.LANCZOS).rotate(-6, resample=Image.BICUBIC)
gol = Image.new('L', (W, H), 0)
ga = k.split()[3].filter(ImageFilter.GaussianBlur(2.2))
gol.paste(ga, (cx - CAP // 2 + 3, cy - CAP // 2 + 4))
gv = np.asarray(gol).astype(np.float32)[..., None] / 255
B = B * (1 - 0.55 * gv)
out = Image.fromarray(B.clip(0, 255).astype(np.uint8)).convert('RGBA')
k = k.filter(ImageFilter.GaussianBlur(0.45))
out.alpha_composite(k, (cx - CAP // 2, cy - CAP // 2))
o = np.asarray(out.convert('RGB')).astype(np.float32)
ka = np.zeros((H, W), np.float32)
ka[cy - CAP // 2:cy + CAP // 2, cx - CAP // 2:cx + CAP // 2] = np.asarray(k.split()[3]) / 255
rng = np.random.default_rng(3)
o += (rng.normal(0, 2.2, (H, W)) * ka)[..., None]
Image.fromarray(o.clip(0, 255).astype(np.uint8)).save('yeni-parti-rozetli.jpg', quality=96, subsampling=0)
print('ok')
