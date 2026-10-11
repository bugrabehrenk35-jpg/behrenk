#!/bin/sh
# Kullanım: sh post-slogan.sh kaynak.html cikti-post.png
# Hikâyeyi slogansız oluşturur, 1080x1440'a genişletir, sloganı gönderinin sağ boşluğuna yerleştirir.
set -e
K=$1; O=$2; T=$(mktemp -d)
sed 's|<body style="|<body class="slogansiz" style="|' "$K" > _gecici.html
sed -i 's|</style>|body.slogansiz .slogan{display:none}</style>|' _gecici.html
node ../../render.mjs _gecici.html $T/s.png 1080 1920
python3 post-yap.py $T/s.png _post-zemin.png
cat > _post.html <<H
<!doctype html><html lang="tr"><meta charset="utf-8"><style>
@font-face{font-family:O7;src:url(../../fontlar-gecici/Oswald-700.ttf)}
html,body{margin:0;width:1080px;height:1440px;overflow:hidden}
body{position:relative;background:url(_post-zemin.png) 0 0/1080px 1440px no-repeat}
.slogan{position:absolute;right:22px;top:${SLOGAN_UST:-712}px;border-left:7px solid #ED1C24;padding:3px 0 5px 18px;
  white-space:nowrap;font:${SLOGAN_BOY:-46}px/1.04 O7;color:#414042}
.slogan em{display:block;font-style:normal;color:#ED1C24}
</style><body><div class="slogan">SÖZ, YETKİ,<br>KARAR<em>ARTIK<br>ÜYELERİMİZİN!</em></div></body></html>
H
node ../../render.mjs _post.html "$O" 1080 1440
rm -rf $T _gecici.html _post.html _post-zemin.png
