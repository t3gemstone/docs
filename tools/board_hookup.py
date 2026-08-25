#!/usr/bin/env python3
"""
T3 Gemstone O1 harici baglanti diyagramlari.

    canbus.svg      on yuz + J26 vurgusu + USB-CAN adaptoru   (eski 36-canbus.png)
    serial-ttl.svg  arka yuz + J21 vurgusu + USB-TTL kablosu  (eski 35-serial-port-ttl-2.png)

Kullanim:
    python3 tools/board_hookup.py

Kart fotograflari yeni revizyondan; adaptor/kablo gorselleri eski PNG'lerden
kirpildi (donanim degismedi). Metinler teknik ad oldugu icin dil ayrimi yok.

Konum birimi
------------
Bilesen yerleri, foto kirpilirken kullanilan olcum cercevesinde (2000px genis
referans) olculdu; asagida kirpik icindeki ORANA cevrilip tuvale tasiniyor.
Yeni bir foto gelirse sadece CROP ve bilesen kutulari guncellenir.
"""

import base64
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
IMG = Path(os.environ.get("BOARD_IMG_DIR", REPO / "images" / "o1-board"))

FONT = ("Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
        "'Helvetica Neue', Arial, sans-serif")
GREEN, INK, EDGE = "#25dd4a", "#141414", "#b9b9b9"

# Kirpik pencereleri (olcum cercevesi birimi): (x0, y0, genislik, yukseklik)
CROP = {
    "front": (399, 185, 1244, 968),      # 43-front-crop.jpg
    "back":  (372, 162, 1226, 981),      # 44-back-crop.jpg
}


def frac(side, x0, y0, x1, y1):
    """Olcum cercevesi kutusunu, kirpik icindeki orana cevirir."""
    cx, cy, cw, ch = CROP[side]
    return ((x0 - cx) / cw, (y0 - cy) / ch, (x1 - cx) / cw, (y1 - cy) / ch)


def embed(name: str) -> str:
    p = IMG / name
    mime = "image/png" if p.suffix == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def head(w, h, title):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}">\n'
        f'  <title>{esc(title)}</title>\n'
        '  <style>\n'
        f'    text {{ font-family: {FONT}; }}\n'
        '    .cap { font-size: 34px; font-weight: 600; fill: #2a2a2a; }\n'
        '    .tagd{ font-size: 30px; font-weight: 700; fill: #fff;\n'
        f'           stroke: {INK}; stroke-width: 13px; stroke-linejoin: round;\n'
        '           paint-order: stroke fill; }\n'
        f'    .zone{{ fill: {GREEN}; fill-opacity: .30; stroke: #0e7a25;\n'
        '           stroke-width: 5; stroke-dasharray: 15 10; }\n'
        f'    .panel {{ fill: #fff; stroke: {EDGE}; stroke-width: 3; }}\n'
        f'    .call {{ fill: none; stroke: {EDGE}; stroke-width: 3; }}\n'
        '  </style>\n'
        f'  <rect width="{w:.0f}" height="{h:.0f}" fill="#fff"/>\n')


def board(name, x, y, w, ratio):
    h = w * ratio
    return (f'  <image x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" '
            f'height="{h:.0f}" xlink:href="{embed(name)}"/>\n'), h


def zone(bx, by, bw, bh, f, pad=0.0):
    """Kirpik oranindan tuval kutusuna; pad orana eklenir."""
    x0 = bx + bw * (f[0] - pad)
    y0 = by + bh * (f[1] - pad)
    x1 = bx + bw * (f[2] + pad)
    y1 = by + bh * (f[3] + pad)
    return x0, y0, x1, y1


# --------------------------------------------------------------------------

def canbus():
    W, H = 2500.0, 1320.0
    BX, BY, BW = 20.0, 25.0, 1600.0
    o = [head(W, H, "T3 Gemstone O1 — CAN Bus")]
    img, BH = board("43-front-crop.jpg", BX, BY, BW, 1162 / 1493)
    o.append(img)

    # J26 (GND / L / H) -- olcum cercevesinde (962,1075)-(1030,1130)
    zx0, zy0, zx1, zy1 = zone(BX, BY, BW, BH,
                              frac("front", 950, 1062, 1042, 1136), pad=.004)
    o.append(f'  <rect class="zone" x="{zx0:.0f}" y="{zy0:.0f}" '
             f'width="{zx1-zx0:.0f}" height="{zy1-zy0:.0f}" rx="7"/>\n')
    o.append(f'  <text class="tagd" x="{(zx0+zx1)/2:.0f}" y="{zy0-22:.0f}" '
             'text-anchor="middle">J26</text>\n')

    # Adaptor paneli
    px, py, pw, ph = 1700.0, 360.0, 760.0, 640.0
    iw = pw - 90
    ih = iw * 179 / 229
    o.append(f'  <rect class="panel" x="{px:.0f}" y="{py:.0f}" '
             f'width="{pw:.0f}" height="{ph:.0f}" rx="14"/>\n')
    o.append(f'  <image x="{px+45:.0f}" y="{py+40:.0f}" width="{iw:.0f}" '
             f'height="{ih:.0f}" xlink:href="{embed("45-usb-can-adapter.png")}"/>\n')
    o.append(f'  <text class="cap" x="{px+pw/2:.0f}" y="{py+ph-42:.0f}" '
             'text-anchor="middle">USB TO CAN ADAPTER</text>\n')

    # Buyutec kama cizgileri: J26 kutusundan panelin alt kenarina
    o.append(f'  <path class="call" d="M {zx1:.0f} {zy0+6:.0f} '
             f'L {px:.0f} {py+ph:.0f}"/>\n')
    o.append(f'  <path class="call" d="M {zx1:.0f} {zy1-6:.0f} '
             f'L {px+pw:.0f} {py+ph:.0f}"/>\n')
    o.append('</svg>\n')
    return "".join(o)


def serial_ttl():
    W, H = 2500.0, 1460.0
    BX, BY, BW = 20.0, 190.0, 1520.0
    o = [head(W, H, "T3 Gemstone O1 — UART / USB-TTL")]
    img, BH = board("44-back-crop.jpg", BX, BY, BW, 1178 / 1472)
    o.append(img)

    # J21 bolgesi -- olcum cercevesinde (556,1012)-(684,1124)
    zx0, zy0, zx1, zy1 = zone(BX, BY, BW, BH,
                              frac("back", 556, 1012, 684, 1124), pad=.006)
    o.append(f'  <rect class="zone" x="{zx0:.0f}" y="{zy0:.0f}" '
             f'width="{zx1-zx0:.0f}" height="{zy1-zy0:.0f}" rx="9"/>\n')

    cx, cy, cw, ch = CROP["back"]
    pin_x = [BX + BW * ((v - cx) / cw) for v in (590, 620, 650)]   # TX GND RX
    pin_y = BY + BH * ((1030 - cy) / ch)

    # Paneller: ustte kablo, altta uc yakin cekimi
    px, pw = 1720.0, 740.0
    o.append(f'  <rect class="panel" x="{px:.0f}" y="40" width="{pw:.0f}" '
             'height="700" rx="14"/>\n'
             f'  <image x="{px+60:.0f}" y="70" width="620" '
             f'height="{620*254/259:.0f}" '
             f'xlink:href="{embed("46-usb-ttl-cable.png")}"/>\n'
             f'  <text class="cap" x="{px+pw/2:.0f}" y="712" '
             'text-anchor="middle">USB to TTL Converter</text>\n')

    IX, IY, IW = px + 60, 795.0, 620.0
    IH = IW * 256 / 257
    o.append(f'  <rect class="panel" x="{px:.0f}" y="770" width="{pw:.0f}" '
             'height="655" rx="14"/>\n'
             f'  <image x="{IX:.0f}" y="{IY:.0f}" width="{IW:.0f}" '
             f'height="{IH:.0f}" '
             f'xlink:href="{embed("47-usb-ttl-pins.png")}"/>\n')

    # Kablo uclarinin panel gorseli icindeki olculmus orani
    tip = {name: (IX + IW * fx, IY + IH * fy) for name, fx, fy in
           (("RXD", .019, .191), ("TXD", .062, .324), ("GND", .093, .449))}

    # Tel yonlendirmesi. UART capraz baglanir: kartin TX'i adaptorun RXD'sine,
    # kartin RX'i adaptorun TXD'sine gider. (Eski gorselde duz gecis cizilmisti,
    # yanlisti -- 2026-08-25'te duzeltildi.)
    # RX'in dikeyi pin grubunun sagina alindi ki kesisimler etiketlerin
    # uzerinde degil, acik alanda olsun.
    PW_, PH_ = 92.0, 52.0
    cxc = pin_x[1]
    pill = [cxc - 98, cxc, cxc + 98]
    ptop, pbot = 1110.0, 1162.0
    lane = pill[2] + PW_ / 2 + 25

    wires = [
        ("RX",  "#f2d000", "#1a1a1a", pill[2], tip["TXD"],
         [(lane, 1136), (lane, tip["TXD"][1])]),
        ("TX",  "#e02020", "#ffffff", pill[0], tip["RXD"],
         [(pill[0], tip["RXD"][1])]),
        ("GND", "#1a1a1a", "#ffffff", pill[1], tip["GND"],
         [(pill[1], tip["GND"][1])]),
    ]
    for name, col, fg, pxc, (tx, ty), mids in wires:
        head_pt = (pxc + PW_ / 2, 1136) if name == "RX" else (pxc, ptop)
        pts = [head_pt] + mids + [(tx, ty)]
        d = "M " + " L ".join(f"{a:.0f} {b:.0f}" for a, b in pts)
        o.append(f'  <path d="{d}" fill="none" stroke="{col}" '
                 'stroke-width="7" stroke-linejoin="round" '
                 'stroke-linecap="round"/>\n')

    # Pin saplari + TX / GND / RX haplari
    order = [("TX", "#e02020", "#ffffff"), ("GND", "#1a1a1a", "#ffffff"),
             ("RX", "#f2d000", "#1a1a1a")]
    for i, (name, col, fg) in enumerate(order):
        o.append(f'  <path d="M {pill[i]:.0f} {pbot:.0f} L {pin_x[i]:.0f} '
                 f'{pin_y:.0f}" stroke="{col}" stroke-width="6" fill="none"/>\n')
    for i, (name, col, fg) in enumerate(order):
        o.append(f'  <rect x="{pill[i]-PW_/2:.0f}" y="{ptop:.0f}" '
                 f'width="{PW_:.0f}" height="{PH_:.0f}" rx="9" fill="{col}" '
                 'stroke="#111" stroke-width="3"/>\n'
                 f'  <text x="{pill[i]:.0f}" y="{ptop+37:.0f}" '
                 f'text-anchor="middle" font-size="30" font-weight="700" '
                 f'fill="{fg}">{name}</text>\n')
    o.append('</svg>\n')
    return "".join(o)


JOBS = {"canbus": canbus, "serial-ttl": serial_ttl}


def main():
    need = ["43-front-crop.jpg", "44-back-crop.jpg", "45-usb-can-adapter.png",
            "46-usb-ttl-cable.png", "47-usb-ttl-pins.png"]
    missing = [n for n in need if not (IMG / n).exists()]
    if missing:
        print("Eksik:", ", ".join(missing), file=sys.stderr)
        return 1
    for name, fn in JOBS.items():
        out = IMG / f"{name}.svg"
        out.write_text(fn(), encoding="utf-8")
        print(f"{out.relative_to(REPO)}  ({out.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
