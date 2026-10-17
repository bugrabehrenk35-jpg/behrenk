# Buğra Behrenk (solda) ve Dilaver Demir (sağda, omzu hafif önde) katmanı; aynı boy, ortak göz hizası.
# Pozlama gömlek beyazından, ten tonu Lab uzayında ortak hedefe eşitlenir.
# Kullanım: python3 kisiler.py [ayar.json] [cikti.png]
import sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as nd
from skimage.color import rgb2lab, lab2rgb

P = dict(
    K=2, W=1080, H=1350,
    beyaz=(234, 235, 241),          # ortak gömlek beyazı
    ten=(65.0, 16.5, 19.0),         # ortak ten hedefi (Lab)
    ten_gucu_b=0.75, ten_gucu_d=0.75,
    bas=320,                          # Dilaver'in baş yüksekliği (saç üstü-çene); Buğra ipd_oran ile ölçeklenir
    ipd_oran=266.4 / 321.9,           # Dilaver/Buğra göz bebeği mesafesi (kaynaklarda ölçüldü)
    goz=388,                          # ortak göz hizası (y)
    d_sol=421,                        # Dilaver gövdesinin sol kenarı x (Buğra'nın sağ kol kesiğini örter)
    golge=0.38,
    b_sol=0,                          # Buğra'nın sol kenarı x
    eri_bas=820, eri_bit=960,
)
if len(sys.argv) > 1 and sys.argv[1].endswith('.json'):
    P.update(json.load(open(sys.argv[1])))
cikti = sys.argv[2] if len(sys.argv) > 2 else 'kisiler.png'
K = P['K']; W, H = P['W'] * K, P['H'] * K

def renk_duzelt(rgb, alfa, gomlek, yuz_kutu, gucu, hedef_ozel=None):
    """rgb: float 0-255. gömlek beyazına göre kanal kazancı, sonra yüz ten tonunu hedefe kaydır."""
    kaz = np.array(P['beyaz'], np.float32) / np.array(gomlek, np.float32)
    x = rgb * kaz
    # parlakları yumuşak sıkıştır (patlama olmasın)
    x = np.where(x > 235, 235 + (x - 235) * 0.45, x)
    lab = rgb2lab(np.clip(x, 0, 255) / 255)
    L, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
    h = np.degrees(np.arctan2(B, A)); C = np.hypot(A, B)
    ten = (alfa > 0.5) & (L > 30) & (L < 93) & (C > 7) & (C < 48) & (h > 12) & (h < 78)
    olc = np.zeros_like(ten)
    for (x0, y0, x1, y1) in (yuz_kutu if isinstance(yuz_kutu[0], (list, tuple)) else [yuz_kutu]):
        olc[y0:y1, x0:x1] = True
    ort = lab[ten & olc].mean(0)
    hedef = np.array(P['ten'] if hedef_ozel is None else hedef_ozel, np.float32)
    fark = (hedef - ort) * gucu
    # deliksiz, yumuşak ten bölgesi: kapat, doldur, bulanıklaştır
    tk = nd.binary_closing(ten, structure=np.ones((15, 15)))
    tk = nd.binary_fill_holes(tk) & (alfa > 0.5)
    tk = nd.binary_opening(tk, structure=np.ones((5, 5)))
    m = np.clip(nd.gaussian_filter(tk.astype(np.float32), 6.0) * 1.15, 0, 1) * (alfa > 0.5)
    lab2 = lab + fark[None, None, :] * m[..., None]
    # ten dışına da a/b farkının küçük bir kısmı: genel uyum
    lab2[..., 1:] += fark[None, None, 1:] * 0.15 * (1 - m)[..., None] * (alfa > 0.5)[..., None]
    out = lab2rgb(lab2) * 255
    print('  gömlek kazancı', kaz.round(3), 'ten ölçülen', ort.round(1), 'kaydırma', fark.round(1))
    return out.astype(np.float32)

def kenar_temizle(rgb, alfa, px, zemin=None):
    """Kesik kenarını eski fon renginden arındırır.
    1) 0<alfa<1 piksellerde ön plan rengini fondan geri çözer: F = (C - (1-a)*Z) / a  (beyaz hale gider, saç teli korunur)
       zemin: (r,g,b) sabit fon ya da None = en yakın tam saydam pikselin kaynaktaki rengi
    2) iç sınırdan px piksellik bantta renk tonunu (a*, b*) içeriden alır, parlaklığı korur (mor/mavi renk saçağı gider)"""
    if px <= 0: return rgb
    a = alfa[..., None]
    if zemin is None:
        dis = alfa < 0.02
        zy, zx = nd.distance_transform_edt(~dis, return_distances=False, return_indices=True)
        Z = rgb[zy, zx]
    else:
        Z = np.array(zemin, np.float32)[None, None, :]
    yari = (alfa > 0.02) & (alfa < 0.98)
    on = rgb.copy()
    on[yari] = np.clip((rgb[yari] - (1 - a[yari]) * (Z[yari] if Z.ndim == 3 and Z.shape[0] > 1 else Z[0, 0])) / np.maximum(a[yari], 0.05), 0, 255)
    ic = nd.binary_erosion(alfa > 0.98, iterations=px)
    iy, ix = nd.distance_transform_edt(~ic, return_distances=False, return_indices=True)
    bant = (alfa > 0.02) & ~ic
    lab = rgb2lab(on[bant][None] / 255)[0]
    labi = rgb2lab(on[iy[bant], ix[bant]][None] / 255)[0]
    lab[:, 0] = np.minimum(lab[:, 0], labi[:, 0] + P.get('kenar_tavan', 3.0))   # içeriden parlak olamaz: hale gider, tel korunur
    lab[:, 1:] = labi[:, 1:]
    on[bant] = np.clip(lab2rgb(lab[None])[0] * 255, 0, 255)
    return on

# --- Dilaver
d = Image.open('/root/.claude/uploads/507a373d-836a-5ae5-b148-f939800e9b37/53e7bdb5-image.png')
d = d.crop((600, 480, 3200, 5374))                     # boşlukları at (ölçüm kutuları buna göre)
da = np.asarray(d)[..., 3].astype(np.float32) / 255
print('Dilaver')
drgb = renk_duzelt(np.asarray(d.convert('RGB')).astype(np.float32), da, (210.1, 210.6, 221.8), P.get('d_kutu', (960, 280, 1660, 1120)), P['ten_gucu_d'])
drgb = kenar_temizle(drgb, da, P.get('kenar_d', 0), P.get('zemin_d', (240, 238, 239)))
D_BAS_UST, D_CENE = 559 - 480, 1625 - 480               # kırpılmış koordinatta saç üstü ve çene
D_BBOX_SOL = 686 - 600
s_d = P['bas'] * K / (D_CENE - D_BAS_UST)
dW, dH = round(d.width * s_d), round(d.height * s_d)
dimg = Image.fromarray(np.dstack([np.clip(drgb, 0, 255), da * 255]).astype(np.uint8), 'RGBA').resize((dW, dH), Image.LANCZOS)
D_GOZ = 1065.5 - 480                                   # kaynakta göz bebekleri hizası (ölçüldü)
dx = round(P['d_sol'] * K - D_BBOX_SOL * s_d); dy = round(P['goz'] * K - D_GOZ * s_d)

# --- Buğra
b = Image.open('/home/user/behrenk/tasarim/kisisel/rozet/yeni-parti-rozetli-hd.jpg').convert('RGB')
ba = np.asarray(Image.open('bugra-maske.png')).astype(np.float32) / 255
print('Buğra')
def ten_olc(rgb, alfa, kutular):
    lab = rgb2lab(np.clip(rgb, 0, 255) / 255)
    m = np.zeros(alfa.shape, bool)
    for (x0, y0, x1, y1) in kutular: m[y0:y1, x0:x1] = True
    L, A, B = lab[..., 0], lab[..., 1], lab[..., 2]; h = np.degrees(np.arctan2(B, A)); C = np.hypot(A, B)
    m &= (alfa > 0.95) & (L > 35) & (L < 92) & (C > 8) & (C < 48) & (h > 12) & (h < 78)
    return lab[m].mean(0)
# Buğra'nın teni, Dilaver'in düzeltilmiş teninin aynı bölgelerine (alın + iki yanak) eşitlenir
d_ten = ten_olc(drgb, da, P['d_olcum']) if P.get('b_dilavere') else None
if d_ten is not None: print('  Dilaver ten (alın+yanak)', d_ten.round(1))
brgb = renk_duzelt(np.asarray(b).astype(np.float32), ba, (240.6, 241.7, 248.0), P.get('b_kutu', (760, 420, 1500, 1300)), P['ten_gucu_b'], hedef_ozel=d_ten if P.get('b_dilavere') else None)
brgb = kenar_temizle(brgb, ba, P.get('kenar_b', 0), None)
B_BAS_UST, B_CENE = 155, 1320
B_GOZ = 715                                            # kaynakta göz bebekleri hizası (ölçüldü)
s_b = s_d * P['ipd_oran']                                  # göz bebeği mesafeleri eşit: yüzler aynı boyda
bW, bH = round(b.width * s_b), round(b.height * s_b)
bimg = Image.fromarray(np.dstack([np.clip(brgb, 0, 255), ba * 255]).astype(np.uint8), 'RGBA').resize((bW, bH), Image.LANCZOS)
if P.get('gren_b', 0):
    arr = np.asarray(bimg).astype(np.float32)
    n = nd.gaussian_filter(np.random.default_rng(7).normal(0, 1, arr.shape[:2]).astype(np.float32), 0.6); n /= n.std()
    arr[..., :3] += n[..., None] * P['gren_b']
    bimg = Image.fromarray(arr.clip(0, 255).astype(np.uint8), 'RGBA')
bx = round(P['b_sol'] * K); by = round(P['goz'] * K - B_GOZ * s_b)   # göz hizası ortak

# --- birleştir
def katman(img, x, y):
    k = Image.new('RGBA', (W, H), (0, 0, 0, 0)); k.paste(img, (x, y)); return k
tuval = katman(bimg, bx, by)
# Dilaver'in Buğra üzerine gölgesi (sağa-aşağı kayık, yumuşak)
dal = Image.new('L', (W, H), 0); dal.paste(dimg.split()[3], (dx, dy))
g = nd.gaussian_filter(nd.shift(np.asarray(dal).astype(np.float32) / 255, (14 * K, -12 * K), order=1), 16 * K)
t = np.asarray(tuval).astype(np.float32)
t[..., :3] *= (1 - P['golge'] * g)[..., None]
tuval = Image.fromarray(t.clip(0, 255).astype(np.uint8), 'RGBA')
tuval.alpha_composite(katman(dimg, dx, dy))
# arka ışık sarması: sıcak fonun ışığı siluet kenarına hafifçe taşar (tek ortamda çekilmiş hissi)
if P.get('sarma', 0):
    t = np.asarray(tuval).astype(np.float32); al = t[..., 3] / 255
    w = np.clip(nd.gaussian_filter(1 - al, P.get('sarma_r', 5) * K) * al * 2, 0, 1)
    w *= np.clip((P.get('sarma_bit', 620) * K - np.arange(H)[:, None]) / (120 * K), 0, 1)   # sadece üst bölge (açık fon)
    renk = np.array(P.get('sarma_renk', (255, 196, 150)), np.float32)
    t[..., :3] = 255 - (255 - t[..., :3]) * (1 - w[..., None] * P['sarma'] * renk / 255)   # screen
    tuval = Image.fromarray(t.clip(0, 255).astype(np.uint8), 'RGBA')
# alt kısımda ikisini de koyu zemine erit (Buğra'nın fotoğrafı göğüste bitiyor)
t = np.asarray(tuval).astype(np.float32)
yy = np.arange(H)[:, None]
eri = np.clip((P['eri_bit'] * K - yy) / ((P['eri_bit'] - P['eri_bas']) * K), 0, 1)
eri = eri * eri * (3 - 2 * eri)
t[..., 3] *= eri
tuval = Image.fromarray(t.clip(0, 255).astype(np.uint8), 'RGBA')
tuval.save(cikti)
print('ok', cikti, 'Dilaver', (dx // K, dy // K, dW // K, dH // K), 'Buğra', (bx // K, by // K, bW // K, bH // K))
