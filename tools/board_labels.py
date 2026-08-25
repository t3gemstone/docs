#!/usr/bin/env python3
"""
T3 Gemstone O1 kart diyagramlarini uretir (on/arka yuz, TR/EN).

Etiketler gercek <text> elemani olarak yazilir; fotograf <image> olarak gomulur.
Konum duzeltmek icin asagidaki FRONT / BACK tablolarindaki sayilari degistir ve
scripti tekrar calistir. Inkscape'te acip elle de tasiyabilirsin -- her etiket
kendi <g id="label-..."> grubunda.

Kullanim:
    python3 tools/board_labels.py

Metin bicimi
------------
Etiket metni tek bir string: satirlar "|" ile ayrilir, *yildiz* arasi kalin.

    "*40-Pin*|Expansion Header"       -> 1. satir kalin, 2. satir normal
    "Display|*HDMI*"                  -> 2. satir kalin  (alt etiket stili)
    "*eMMC* 32 GB"                    -> tek satir, karisik agirlik
    "*Usb 2.0*|1x Type-A &|1x Type-C" -> uc satir

Etiketler kuyruklu siyah balon icinde. Balon genisligi metnin PIL ile olculen
genisliginden hesaplanir; SVG tarafinda textLength ile ayni genislige zorlanir,
boylece okuyucunun fontu farkli olsa da metin balona tam oturur.

Koordinat sistemi
-----------------
Tum koordinatlar, fotografin 2000px genislige olceklendigi bir tuval icindir.
Fotograf tuvalde (PHOTO_X, PHOTO_Y) noktasina konur; kenarlarda etiket boslugu
kalir. Fotografin gercek pikseli onemsizdir, en/boy orani onemlidir (~3:2).
"""

import base64
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
IMG = Path(os.environ.get("BOARD_IMG_DIR", REPO / "images" / "o1-board"))

PHOTO_W = 2000.0
PHOTO_X, PHOTO_Y = 300.0, 120.0
CANVAS_W, CANVAS_H = 2600.0, 1580.0

LINE = "#2b7fa8"          # ok cizgileri
DOT = "#8ecfe8"           # bilesen uzerindeki nokta
INK = "#141414"           # sticker zemini
PAPER = "#ffffff"

FS = 42                   # temel punto
LINE_GAP = 50             # satir araligi
PAD_X, PAD_Y = 26.0, 17.0   # balon ic boslugu
ASC, DESC = 32.0, 10.0      # FS icin ust/alt yazi payi
RX = 15                     # balon kose yaricapi
TAIL = 15                   # kuyruk ucgeni yarim genisligi
DOT_R = 18
LEAD_W = 4

# Dokumanlarin govde fontu Inter (bkz. docs.json / fonts.css). SVG bir <img>
# icinde ayri belge olarak render edildigi icin harici font YUKLEYEMEZ; bu
# yuzden once yerel Inter denenir, yoksa gorsel olarak cok yakin olan sistem
# grotesk'ine dusulur.
FONT = ("Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
        "'Helvetica Neue', Arial, sans-serif")


# --------------------------------------------------------------------------
# Etiket tablolari
#
#   id   : SVG grup adi (Inkscape'te bu isimle gorunur)
#   at   : etiket blogunun ILK satirinin merkez noktasi (x, y)
#   path : etiketten bilesene giden kirik cizginin ara noktalari
#   dot  : bilesenin uzerindeki nokta (x, y)
# --------------------------------------------------------------------------

FRONT = [
    dict(id="gpio40", at=(960, 200),
         en="*40-Pin*|Expansion Header",
         tr="*40-Pin*|Genişletme Konnektörü",
         path=[(960, 310), (1090, 310)], dot=(1090, 382)),

    dict(id="soc", at=(1463, 110),
         en="*System On Chip*|Texas AM67A",
         tr="*Sistem Yongası*|Texas AM67A",
         path=[(1463, 185)], dot=(1463, 609)),

    dict(id="fan", at=(1850, 200),
         en="*Fan*|*Connector*",
         tr="*Fan*|*Konnektörü*",
         path=[(1850, 300), (1507, 300)], dot=(1507, 354)),

    dict(id="wifi", at=(460, 470),
         en="*WIFI + Bluetooth*|Fn-Link 6222B-SRC",
         tr="*WiFi + Bluetooth*|Fn-Link 6222B-SRC",
         path=[(460, 545), (460, 605), (868, 605)], dot=(888, 605)),

    dict(id="emmc", at=(460, 730),
         en="*eMMC* 32 GB",
         tr="*eMMC* 32 GB",
         path=[(460, 752), (460, 795), (1160, 795)], dot=(1180, 795)),

    dict(id="rtc", at=(400, 960),
         en="*RTC (Realtime Clock)*|Battery",
         tr="*RTC (Gerçek Zamanlı Saat)*|Pil",
         path=[(400, 1005), (400, 1018), (723, 1018)], dot=(743, 1018)),

    dict(id="usb3", at=(2270, 330),
         en="*Usb 3.0*|2x Type-A",
         tr="*Usb 3.0*|2x Type-A",
         path=[(2270, 400), (2270, 431), (1839, 431)], dot=(1819, 431)),

    dict(id="debug", at=(2270, 640),
         en="*Debug*|Plug of Nails JTAG",
         tr="*Hata Ayıklama*|Plug of Nails JTAG",
         path=[(2270, 600), (2270, 560), (1843, 560)], dot=(1823, 560)),

    dict(id="usb2", at=(2270, 820),
         en="*Usb 2.0*|1x Type-A &|1x Type-C",
         tr="*Usb 2.0*|1x Type-A &|1x Type-C",
         path=[(2270, 780), (2270, 744), (1835, 744)], dot=(1815, 744)),

    dict(id="network", at=(2270, 1060),
         en="*Network*|Ethernet Gigabit",
         tr="*Ağ*|Gigabit Ethernet",
         path=[(2270, 1132), (2270, 1145), (1800, 1145)], dot=(1780, 1145)),

    dict(id="usbc", at=(637, 1340),
         en="USB-C|*Power&Console*",
         tr="USB-C|*Güç ve Konsol*",
         path=[(637, 1260), (872, 1260)], dot=(872, 1205)),

    dict(id="extpower", at=(971, 1340),
         en="External|*Power*",
         tr="Harici|*Güç*",
         path=[(971, 1250), (995, 1250)], dot=(995, 1210)),

    dict(id="hdmi", at=(1213, 1340),
         en="Display|*HDMI*",
         tr="Ekran|*HDMI*",
         path=[(1213, 1255), (1138, 1255)], dot=(1138, 1205)),

    dict(id="canbus", at=(1487, 1340),
         en="Peripheral|*CanBUS*",
         tr="Çevre Birim|*CanBUS*",
         path=[(1487, 1265), (1301, 1265)], dot=(1301, 1222)),

    dict(id="csidsi", at=(1841, 1340),
         en="Camera/Display|*4-Line DSI/CSI*",
         tr="Kamera/Ekran|*4-Hat DSI/CSI*",
         path=[(1841, 1190), (1400, 1190)], dot=(1400, 1150)),
]

FRONT_REGIONS = [
    (798, 333, 1385, 432),     # J23 40-pin header
    (1785, 530, 1862, 590),    # J2 debug JTAG
    (1365, 1075, 1510, 1235),  # J11 / J12 CSI-DSI
]

BACK = [
    dict(id="bootmode", at=(1405, 200),
         en="*Switch*|Boot Mode",
         tr="*Anahtar*|Önyükleme Modu",
         path=[(1405, 275)], dot=(1405, 393)),

    dict(id="sdcard", at=(450, 655),
         en="*Storage*|SD-Card Slot",
         tr="*Depolama*|SD Kart Yuvası",
         path=[(450, 700), (450, 716), (747, 716)], dot=(767, 716)),

    dict(id="m2", at=(2200, 860),
         en="*Storage*|M.2 SSD Slot",
         tr="*Depolama*|M.2 SSD Yuvası",
         path=[(2200, 932), (2200, 942), (1470, 942)], dot=(1450, 942)),

    dict(id="uart", at=(920, 1400),
         en="*UART*|Console/TTL",
         tr="*UART*|Konsol/TTL",
         path=[(920, 1368), (920, 1186)], dot=(920, 1166)),
]

BACK_REGIONS = [
    (1230, 320, 1535, 455),   # SW2 / SW3 boot mode anahtarlari
    (815, 808, 1690, 1077),   # J20 M.2 alani
]


# --------------------------------------------------------------------------

def photo_size(path: Path):
    """Fotografin piksel boyutunu dondurur (sips, macOS)."""
    out = subprocess.run(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
        capture_output=True, text=True, check=True).stdout
    dims = {}
    for line in out.splitlines():
        k, _, v = line.strip().partition(":")
        if k in ("pixelWidth", "pixelHeight"):
            dims[k] = int(v)
    return dims["pixelWidth"], dims["pixelHeight"]


def embed(path: Path) -> str:
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return (f"data:{mime};base64,"
            + base64.b64encode(path.read_bytes()).decode("ascii"))


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def parse(spec: str):
    """'a|*b* c' -> [[('a','r')], [('b','b'), (' c','r')]]"""
    return [[(part, "b" if i % 2 else "r")
             for i, part in enumerate(re.split(r"\*", raw)) if part]
            for raw in spec.split("|")]


# Balon genisligi Arial metrigiyle olculur. Okuyucunun tarayicisi Inter,
# SF Pro, Segoe UI, Roboto ya da Helvetica kullanabilir; bunlarin hicbiri
# Arial'dan %10'dan fazla genis degil, bu yuzden olcume SAFE kadar pay eklenir.
# (textLength ile zorlamak denendi ama bazi renderer'lar yok sayip metni
# balonun disina tasiriyor -- pay eklemenin basarisiz olma ihtimali yok.)
SAFE = 1.10
_FACE = {"b": "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
         "r": "/System/Library/Fonts/Supplemental/Arial.ttf"}
_cache = {}


def _font(weight):
    if weight not in _cache:
        from PIL import ImageFont
        _cache[weight] = ImageFont.truetype(_FACE[weight], FS)
    return _cache[weight]


def text_w(segs) -> float:
    """Bir satirin dogal genisligi (px). Agirliga gore ayri ayri olculur."""
    return sum(_font(w).getlength(t) for t, w in segs) * SAFE


def label_box(lb, lang):
    """Balonun (x0, y0, x1, y1) kutusu ve satir genislikleri."""
    x, y = lb["at"]
    lines = parse(lb[lang])
    widths = [text_w(sg) for sg in lines]
    bw = max(widths) + 2 * PAD_X
    x0 = x - bw / 2
    y0 = y - ASC - PAD_Y
    y1 = y + (len(lines) - 1) * LINE_GAP + DESC + PAD_Y
    return (x0, y0, x0 + bw, y1), lines, widths


def _attach(box, pts):
    """Balonun hangi kenarindan cikilacagi + kuyruk ucgeni.

    Kutunun ICINDE kalan yol noktalari atilir; ilk disaridaki noktaya gore
    kenar secilir. Boylece yol tablosundaki sayilar degismeden kuyruk
    kendiliginde dogru yere oturur.
    """
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    outside = [p for p in pts
               if not (x0 <= p[0] <= x1 and y0 <= p[1] <= y1)]
    if not outside:
        outside = [pts[-1]]
    tx, ty = outside[0]

    if ty >= y1:
        side, ax, ay = "b", min(max(tx, x0 + RX + 12), x1 - RX - 12), y1
        tip, base = (ax, ay + TAIL), [(ax - TAIL, ay), (ax + TAIL, ay)]
    elif ty <= y0:
        side, ax, ay = "t", min(max(tx, x0 + RX + 12), x1 - RX - 12), y0
        tip, base = (ax, ay - TAIL), [(ax - TAIL, ay), (ax + TAIL, ay)]
    elif tx >= x1:
        ay = min(max(ty, y0 + RX + 10), y1 - RX - 10)
        tip, base = (x1 + TAIL, ay), [(x1, ay - TAIL), (x1, ay + TAIL)]
    else:
        ay = min(max(ty, y0 + RX + 10), y1 - RX - 10)
        tip, base = (x0 - TAIL, ay), [(x0, ay - TAIL), (x0, ay + TAIL)]
    return tip, base, outside


def render_label(lb: dict, lang: str) -> str:
    x, y = lb["at"]
    box, lines, widths = label_box(lb, lang)
    x0, y0, x1, y1 = box
    tip, base, outside = _attach(box, list(lb["path"]) + [lb["dot"]])

    d = "M " + " L ".join(f"{a:.0f} {b:.0f}"
                          for a, b in [tip] + outside + [lb["dot"]])
    dx, dy = lb["dot"]

    txt = []
    for i, segs in enumerate(lines):
        run = "".join(f'<tspan class="{wt}">{esc(t)}</tspan>' for t, wt in segs)
        txt.append(f'<text x="{x:.0f}" y="{y + i * LINE_GAP:.0f}" '
                   f'text-anchor="middle" class="lbl">{run}</text>')

    tri = " ".join(f"{a:.0f},{b:.0f}" for a, b in [tip] + base)
    return (f'    <g id="label-{lb["id"]}">\n'
            f'      <path class="lead" d="{d}"/>\n'
            f'      <circle class="dot" cx="{dx:.0f}" cy="{dy:.0f}" r="{DOT_R}"/>\n'
            f'      <polygon class="balloon" points="{tri}"/>\n'
            f'      <rect class="balloon" x="{x0:.0f}" y="{y0:.0f}" '
            f'width="{x1-x0:.0f}" height="{y1-y0:.0f}" rx="{RX}"/>\n'
            f'      {"".join(txt)}\n'
            f'    </g>\n')


def build(photo: Path, labels, regions, lang: str, title: str) -> str:
    pw, ph = photo_size(photo)
    draw_h = ph * (PHOTO_W / pw)

    if not 1.35 < pw / ph < 1.65:
        print(f"  ! {photo.name} orani {pw / ph:.2f} — beklenen ~1.50. "
              "Etiketler dikeyde kaymis olabilir.", file=sys.stderr)

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {CANVAS_W:.0f} {CANVAS_H:.0f}" '
        f'width="{CANVAS_W:.0f}" height="{CANVAS_H:.0f}">\n',
        f'  <title>{esc(title)}</title>\n',
        '  <style>\n'
        f'    .lbl {{ font-family: {FONT}; font-size: {FS}px; fill: {PAPER}; }}\n'
        f'    .balloon {{ fill: {INK}; }}\n'
        '    .lbl .b { font-weight: 700; }\n'
        '    .lbl .r { font-weight: 400; }\n'
        f'    .lead {{ fill: none; stroke: {LINE}; stroke-width: {LEAD_W}; }}\n'
        f'    .dot  {{ fill: {DOT}; opacity: .85; }}\n'
        f'    .zone {{ fill: none; stroke: {LINE}; stroke-width: {LEAD_W};\n'
        '             stroke-dasharray: 18 13; }\n'
        '  </style>\n',
        f'  <rect width="{CANVAS_W:.0f}" height="{CANVAS_H:.0f}" fill="{PAPER}"/>\n',
        f'  <image id="board-photo" x="{PHOTO_X:.0f}" y="{PHOTO_Y:.0f}" '
        f'width="{PHOTO_W:.0f}" height="{draw_h:.0f}" '
        f'xlink:href="{embed(photo)}"/>\n',
    ]

    if regions:
        parts.append('  <g id="zones">\n')
        parts += [f'    <rect class="zone" x="{a}" y="{b}" width="{c - a}" '
                  f'height="{d - b}" rx="6"/>\n' for a, b, c, d in regions]
        parts.append('  </g>\n')

    parts.append('  <g id="labels">\n')
    parts += [render_label(lb, lang) for lb in labels]
    parts.append('  </g>\n</svg>\n')
    return "".join(parts)


JOBS = [
    ("40-front-raw.jpg", FRONT, FRONT_REGIONS, "front"),
    ("41-back-raw.jpg", BACK, BACK_REGIONS, "back"),
]

TITLES = {
    ("front", "en"): "T3 Gemstone O1 — Front Side",
    ("front", "tr"): "T3 Gemstone O1 — Ön Yüz",
    ("back", "en"): "T3 Gemstone O1 — Back Side",
    ("back", "tr"): "T3 Gemstone O1 — Arka Yüz",
}


def main():
    missing = [n for n, *_ in JOBS if not (IMG / n).exists()]
    if missing:
        print("Eksik fotograf(lar):", file=sys.stderr)
        for n in missing:
            print(f"  {IMG / n}", file=sys.stderr)
        return 1

    for name, labels, regions, side in JOBS:
        for lang in ("en", "tr"):
            out = IMG / f"{side}-annotated-{lang}.svg"
            out.write_text(build(IMG / name, labels, regions, lang,
                                 TITLES[(side, lang)]), encoding="utf-8")
            try:
                rel = out.relative_to(REPO)
            except ValueError:
                rel = out
            print(f"{rel}  ({out.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
