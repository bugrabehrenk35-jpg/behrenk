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
    bas=305,                          # ikisinin de baş yüksekliği (saç üstü-çene), aynı boy
    goz=388,                          # ortak göz hizası (y)
    d_sol=457,                        # Dilaver gövdesinin sol kenarı x (Buğra'nın sağ kol kesiğini örter)
    golge=0.38,
    b_sol=0,                          # Buğra'nın sol kenarı x
    eri_bas=850, eri_bit=975,
)
if len(sys.argv) > 1 and sys.argv[1].endswith('.json'):
    P.update(json.load(open(sys.argv[1])))
cikti = sys.argv[2] if len(sys.argv) > 2 else 'kisiler.png'
K = P['K']; W, H = P['W'] * K, P['H'] * K

def renk_duzelt(rgb, alfa, gomlek, yuz_kutu, gucu):
    """rgb: float 0-255. gömlek beyazına göre kanal kazancı, sonra yüz ten tonunu hedefe kaydır."""
    kaz = np.array(P['beyaz'], np.float32) / np.array(gomlek, np.float32)
    x = rgb * kaz
    # parlakları yumuşak sıkıştır (patlama olmasın)
    x = np.where(x > 235, 235 + (x - 235) * 0.45, x)
    lab = rgb2lab(np.clip(x, 0, 255) / 255)
    L, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
    h = np.degrees(np.arctan2(B, A)); C = np.hypot(A, B)
    ten = (alfa > 0.5) & (L > 30) & (L < 93) & (C > 7) & (C < 48) & (h > 12) & (h < 78)
    x0, y0, x1, y1 = yuz_kutu
    olc = np.zeros_like(ten); olc[y0:y1, x0:x1] = True
    ort = lab[ten & olc].mean(0)
    hedef = np.array(P['ten'], np.float32)
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

# --- Dilaver
d = Image.open('/root/.claude/uploads/507a373d-836a-5ae5-b148-f939800e9b37/53e7bdb5-image.png')
d = d.crop((600, 480, 3200, 5374))                     # boşlukları at (ölçüm kutuları buna göre)
da = np.asarray(d)[..., 3].astype(np.float32) / 255
print('Dilaver')
drgb = renk_duzelt(np.asarray(d.convert('RGB')).astype(np.float32), da, (210.1, 210.6, 221.8), (960, 280, 1660, 1120), P['ten_gucu_d'])
D_BAS_UST, D_CENE = 559 - 480, 1625 - 480               # kırpılmış koordinatta saç üstü ve çene
D_BBOX_SOL = 686 - 600
s_d = P['bas'] * K / (D_CENE - D_BAS_UST)
dW, dH = round(d.width * s_d), round(d.height * s_d)
dimg = Image.fromarray(np.dstack([np.clip(drgb, 0, 255), da * 255]).astype(np.uint8), 'RGBA').resize((dW, dH), Image.LANCZOS)
D_GOZ = 1070 - 480                                     # kaynakta göz hizası (ölçüldü)
dx = round(P['d_sol'] * K - D_BBOX_SOL * s_d); dy = round(P['goz'] * K - D_GOZ * s_d)

# --- Buğra
b = Image.open('/home/user/behrenk/tasarim/kisisel/rozet/yeni-parti-rozetli-hd.jpg').convert('RGB')
ba = np.asarray(Image.open('bugra-maske.png')).astype(np.float32) / 255
print('Buğra')
brgb = renk_duzelt(np.asarray(b).astype(np.float32), ba, (240.6, 241.7, 248.0), (760, 420, 1500, 1300), P['ten_gucu_b'])
B_BAS_UST, B_CENE = 155, 1320
B_GOZ = 720
s_b = P['bas'] * K / (B_CENE - B_BAS_UST)
bW, bH = round(b.width * s_b), round(b.height * s_b)
bimg = Image.fromarray(np.dstack([np.clip(brgb, 0, 255), ba * 255]).astype(np.uint8), 'RGBA').resize((bW, bH), Image.LANCZOS)
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
# alt kısımda ikisini de koyu zemine erit (Buğra'nın fotoğrafı göğüste bitiyor)
t = np.asarray(tuval).astype(np.float32)
yy = np.arange(H)[:, None]
eri = np.clip((P['eri_bit'] * K - yy) / ((P['eri_bit'] - P['eri_bas']) * K), 0, 1)
t[..., 3] *= eri
tuval = Image.fromarray(t.clip(0, 255).astype(np.uint8), 'RGBA')
tuval.save(cikti)
print('ok', cikti, 'Dilaver', (dx // K, dy // K, dW // K, dH // K), 'Buğra', (bx // K, by // K, bW // K, bH // K))
