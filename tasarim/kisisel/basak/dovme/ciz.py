# Başak dövmesi konseptleri. Ölçek: 100 px = 1 cm. İnce çizgi (fineline) ~0,3 mm.
import math
SW=3.0
def P(x,y): return f'{x:.1f},{y:.1f}'
def tane(x,y,ang,L,W,ic=True):
    a=math.radians(ang); dx,dy=math.cos(a),math.sin(a); nx,ny=-dy,dx
    t=(x+dx*L,y+dy*L)
    c1=(x+dx*L*.42+nx*W*.6, y+dy*L*.42+ny*W*.6)
    c2=(x+dx*L*.42-nx*W*.6, y+dy*L*.42-ny*W*.6)
    s=f'<path d="M{P(x,y)} Q{P(*c1)} {P(*t)} Q{P(*c2)} {P(x,y)}Z" fill="#fff" stroke="#111" stroke-width="{SW}" stroke-linejoin="round"/>'
    if ic: s+=f'<path d="M{P(x+dx*L*.2,y+dy*L*.2)} L{P(x+dx*L*.7,y+dy*L*.7)}" stroke="#111" stroke-width="{SW*.55:.2f}" stroke-linecap="round"/>'
    return s,t
def yol(pts,w=SW,dash=None):
    d='M'+' L'.join(P(*p) for p in pts)
    da=f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="none" stroke="#111" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{da}/>'
def kilcik(x,y,ang,L,bukum=0):
    a=math.radians(ang); pts=[]
    for i in range(21):
        u=i/20; aa=a+math.radians(bukum)*u
        pts.append((x+math.cos(aa)*L*u, y+math.sin(aa)*L*u))
    return yol(pts,w=SW*.6)
def basak(eksen, tlist, aci=26, kil=True, kil_L=110):
    """eksen(t)->(x,y), t: 0 dip 1 uç. tlist: [(t,L,W)] alttan üste, taraf dönüşümlü"""
    g=[yol([eksen(i/80) for i in range(81)])]
    taraf=1; ucs=[]
    for i,(t,L,W) in enumerate(tlist):
        x,y=eksen(t); x2,y2=eksen(min(t+.01,1)); ea=math.degrees(math.atan2(y2-y,x2-x))
        s,u=tane(x,y,ea+taraf*aci,L,W); g.append(s); ucs.append((u,ea+taraf*aci)); taraf*=-1
    if kil:
        for (u,a) in ucs[-5:]:
            g.append(kilcik(u[0],u[1],a+(-6 if a<-90 else 6),kil_L*.8,0))
        x,y=eksen(1); x2,y2=eksen(.99); ea=math.degrees(math.atan2(y-y2,x-x2))
        g.append(kilcik(x,y,ea,kil_L))
    return g
def yildiz5(cx,cy,r,dolu=True,don=0):
    pts=[]
    for i in range(10):
        a=math.radians(-90+don+i*36); rr=r if i%2==0 else r*.42
        pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
    d='M'+' L'.join(P(*p) for p in pts)+'Z'
    return f'<path d="{d}" fill="{"#111" if dolu else "none"}" stroke="#111" stroke-width="{max(2.4,r*.16) if dolu else SW}" stroke-linejoin="round"/>'
def yildiz(cx,cy,r):
    pts=[]
    for i in range(8):
        a=math.radians(-90+i*45); rr=r if i%2==0 else r*.26
        pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
    return f'<path d="M{" L".join(P(*p) for p in pts)}Z" fill="#111"/>'

def mors():
    kod=['-...','.-','...','.-','-.-']   # B A S A K (Ş yerine S, açıklamaya bak)
    eksen=lambda t:(350+14*math.sin(t*2.6)-6*t, 760-680*t)
    tl=[]; t=.25; ad=.036; lg=.05
    for h in kod:
        for s in h:
            tl.append((t, 66 if s=='-' else 34, 22 if s=='-' else 21)); t+=ad
        t+=lg
    g=basak(eksen,tl,aci=24,kil=True,kil_L=95)
    return g
def spika():
    eksen=lambda t:(200+36*t+22*math.sin(t*2), 770-400*t)
    tl=[(.40+i*.07,52-i*2.6,24) for i in range(9)]
    g=basak(eksen,tl,aci=30,kil=False)
    x,y=eksen(1)
    g.append(f'<path d="M{P(x,y-6)} Q{P(x+30,y-190)} {P(x+200,y-268)}" fill="none" stroke="#111" stroke-width="2.6" stroke-linecap="round" stroke-dasharray="0.1 13"/>')
    g.append(yildiz(x+224,y-280,30))
    for dx,dy,r in [(300,-215,6),(150,-330,5),(320,-320,4.5),(60,-300,4)]:
        g.append(f'<circle cx="{x+dx:.1f}" cy="{y+dy:.1f}" r="{r}" fill="#111"/>')
    return g
def tohum():
    zem=640; g=[yol([(30,zem),(670,zem)],w=2.2)]
    s,_=tane(55,zem-12,-8,56,32); g.append(s)
    g.append(yol([(220+2*math.sin(u*3),zem-90*u) for u in [i/20 for i in range(21)]]))
    s,_=tane(221,zem-60,-55,38,20,ic=False); g.append(s)
    s,_=tane(219,zem-48,-128,30,18,ic=False); g.append(s)
    e3=lambda t:(380+6*math.sin(t*2), zem-260*t)
    g+=basak(e3,[(.6+i*.09,36,20) for i in range(5)],aci=28,kil=True,kil_L=50)
    e4=lambda t:(560+50*t*t, zem-470*t+30*t*t)
    g+=basak(e4,[(.5+i*.058,46,24) for i in range(9)],aci=28,kil=True,kil_L=85)
    return g
for ad,f in (('A',mors),('B',spika),('C',tohum)):
    g=f()
    open(f'konsept-{ad}.svg','w').write('<svg xmlns="http://www.w3.org/2000/svg" width="700" height="800" viewBox="0 0 700 800">'+''.join(g)+'</svg>')
print('ok')

# ---------- A+B: Gizli isimli başak, kendi yıldızına uzanır
def birlesik(kil_L=60, egim=1.0, bes=None):
    kod=['-...','.-','...','.-','-.-']
    eksen=lambda t:(240+60*t*t*egim+10*math.sin(t*2.4), 790-500*t)
    tl=[]; t=.22; ad=.037; lg=.046
    for h in kod:
        for s in h:
            tl.append((t, 66 if s=='-' else 36, 22 if s=='-' else 21)); t+=ad
        t+=lg
    g=basak(eksen,tl,aci=24,kil=False)
    ucs=[]
    # üstteki tanelerden kısa kılçıklar
    x,y=eksen(1)
    g.append(f'<path d="M{P(x,y-4)} Q{P(x+18,y-150)} {P(x+190,y-200)}" fill="none" stroke="#111" stroke-width="2.6" stroke-linecap="round" stroke-dasharray="0.1 12"/>')
    sx,sy=x+214,y-206
    if bes is None:
        g.append(yildiz(sx,sy,30))
        for dx,dy,r in [(84,-40,5.5),(-140,6,4.5),(70,92,4),(128,44,4)]:
            g.append(f'<circle cx="{sx+dx:.1f}" cy="{sy+dy:.1f}" r="{r}" fill="#111"/>')
    else:
        g.append(yildiz5(sx,sy,32,dolu=bes,don=-6))
        for dx,dy,r,dn in [(66,-50,13,8),(-136,10,10,-8),(58,88,8,10),(-62,64,6,-4)]:
            g.append(yildiz5(sx+dx,sy+dy,r,dolu=True,don=dn))
    return g
g=birlesik()
def etiketli():
    kod=['-...','.-','...','.-','-.-']; harfler='BAŞAK'
    eksen=lambda t:(240+60*t*t+10*math.sin(t*2.4), 790-500*t)
    e=[]; t=.22; ad=.037; lg=.046
    for h,c in zip(kod,harfler):
        t0=t; t+=ad*len(h); t1=t-ad; t+=lg
        x0,y0=eksen(t0); x1,y1=eksen(t1+.03)
        e.append(f'<path d="M{P(x0-60,y0)} L{P(x0-70,y0)} L{P(x1-70,y1)} L{P(x1-60,y1)}" fill="none" stroke="#A8402F" stroke-width="2"/>')
        e.append(f'<text x="{x0-84:.1f}" y="{(y0+y1)/2+9:.1f}" text-anchor="end" font-family="sans-serif" font-size="26" fill="#A8402F">{c}  {h.replace("-","−").replace(".","·")}</text>')
    return e
open('konsept-AB-aciklamali.svg','w').write('<svg xmlns="http://www.w3.org/2000/svg" width="700" height="800" viewBox="0 0 700 800">'+''.join(g+etiketli())+'</svg>')
open('konsept-AB.svg','w').write('<svg xmlns="http://www.w3.org/2000/svg" width="440" height="780" viewBox="190 14 440 780">'+''.join(g)+'</svg>')
print('AB ok')

for ad,b in (('AB-yildiz-dolu',True),('AB-yildiz-cizgi',False)):
    open(f'konsept-{ad}.svg','w').write('<svg xmlns="http://www.w3.org/2000/svg" width="460" height="780" viewBox="190 14 460 780">'+''.join(birlesik(bes=b))+'</svg>')
print('yildiz ok')
