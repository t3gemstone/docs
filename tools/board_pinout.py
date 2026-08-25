#!/usr/bin/env python3
"""
T3 Gemstone O1 40-pin header diyagramlarini uretir.

Tek bir pin tablosundan dort varyant cikar:

    gpio-pinout.svg   tum pinler normal          (eski 32-gpio.png)
    gpio-serial.svg   UART pinleri vurgulu       (eski 33-serials.png)
    gpio-i2c.svg      I2C pinleri vurgulu        (eski 37-i2c.png)
    gpio-pwm.svg      PWM pinleri vurgulu        (eski 38-pwm.png)

Kullanim:
    python3 tools/board_pinout.py

Dil ayrimi yok: tablodaki her sey teknik ad (GPIO-2, I2C-MCU0 SDA), ceviriye
konu degil. Tek dosya hem tr/ hem en/ tarafindan kullanilir.

Sari fonksiyon etiketleri, siyah kart etiketleriyle ayni teknikle ciziliyor:
metnin etrafina kalin bir stroke atilip paint-order ile arkaya gonderiliyor.
Boylece etiket genisligini hesaplamak gerekmiyor, metin degisince zemin uyuyor.
Sabit genislikteki pin kutulari ve isim hapları ise gercek <rect>.
"""

import base64
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
IMG = Path(os.environ.get("BOARD_IMG_DIR", REPO / "images" / "o1-board"))
PHOTO = "42-front-rot.jpg"

# --------------------------------------------------------------------------
# Pin tablosu -- 32-gpio.png'den birebir aktarildi.
#
#   (pin, tur, ad, fonksiyon-etiketi)
#   tur: v33 | v5 | gnd | gpio
#
# NOT: pin 27 ve pin 35 orijinal gorselde de ayni etiketi ("I2C-WKUP0 SDA")
# tasiyor. Muhtemelen pin 35 SCL olmali; kaynagi dogrulanmadigi icin oldugu
# gibi birakildi -- duzeltilecekse tek yer burasi.
# --------------------------------------------------------------------------

PINS = [
    (1,  "v33",  "3v3 Power", None),           (2,  "v5",   "5V Power", None),
    (3,  "gpio", "GPIO-2",  "I2C-MCU0 SDA"),   (4,  "v5",   "5V Power", None),
    (5,  "gpio", "GPIO-3",  "I2C-MCU0 SCL"),   (6,  "gnd",  "GND", None),
    (7,  "gpio", "GPIO-4",  None),             (8,  "gpio", "GPIO-14", "UART-MAIN1 TX"),
    (9,  "gnd",  "GND", None),                 (10, "gpio", "GPIO-15", "UART-MAIN1 RX"),
    (11, "gpio", "GPIO-17", None),             (12, "gpio", "GPIO-18", "PCM-McASP0 CLK"),
    (13, "gpio", "GPIO-27", None),             (14, "gnd",  "GND", None),
    (15, "gpio", "GPIO-22", None),             (16, "gpio", "GPIO-23", None),
    (17, "v33",  "3v3 Power", None),           (18, "gpio", "GPIO-24", None),
    (19, "gpio", "GPIO-10", "SPI-MCU0 MOSI"),  (20, "gnd",  "GND", None),
    (21, "gpio", "GPIO-9",  "SPI-MCU0 MISO"),  (22, "gpio", "GPIO-25", None),
    (23, "gpio", "GPIO-11", "SPI-MCU0 SCLK"),  (24, "gpio", "GPIO-8",  "SPI-MCU0 CS0"),
    (25, "gnd",  "GND", None),                 (26, "gpio", "GPIO-7",  "SPI-MCU0 CS2"),
    (27, "gpio", "GPIO-0",  "I2C-WKUP0 SDA"),  (28, "gpio", "GPIO-1",  "I2C-WKUP0 SCL"),
    (29, "gpio", "GPIO-5",  None),             (30, "gnd",  "GND", None),
    (31, "gpio", "GPIO-6",  None),             (32, "gpio", "GPIO-12", "PWM-ECAP0"),
    (33, "gpio", "GPIO-13", "PWM-1B"),         (34, "gnd",  "GND", None),
    (35, "gpio", "GPIO-19", "I2C-WKUP0 SDA"),  (36, "gpio", "GPIO-16", None),
    (37, "gpio", "GPIO-26", None),             (38, "gpio", "GPIO-20", "PCM-McASP0 DIN"),
    (39, "gnd",  "GND", None),                 (40, "gpio", "GPIO-21", "PCM-McASP0 DOUT"),
]

# Varyantlar: {pin: vurguluyken gosterilecek etiket (None = etiket yok)}
VARIANTS = {
    "gpio-pinout": {},
    "gpio-serial": {7: None, 8: "UART-MAIN1 TX", 10: "UART-MAIN1 RX",
                    11: None, 18: None, 26: None},
    "gpio-i2c":    {3: "I2C-MCU0 SDA", 5: "I2C-MCU0 SCL"},
    "gpio-pwm":    {8: None, 12: None, 29: None, 31: None,
                    32: "PWM-ECAP0", 33: "PWM-1B", 36: None},
}

# --------------------------------------------------------------------------
# Yerlesim
# --------------------------------------------------------------------------

CW, CH = 2500.0, 1560.0
BX, BY, BW, BH = 25.0, 110.0, 1011.0, 1300.0         # kart fotografi
HDR = (841 / 968, 99 / 1244, 940 / 968, 686 / 1244)  # J23'un foto icindeki orani

PANEL = (1240.0, 100.0, 1230.0, 1360.0)
CX = 1855.0                    # pin sutunu ekseni
PIN_W, PIN_H = 62.0, 58.0
ROW0, ROW_DY = 175.0, 64.0
NAME_W, NAME_H = 230.0, 46.0
NAME_GAP = 76.0                # pin kutusu ile isim hapi arasi
TAG_GAP = 26.0                 # isim hapi ile fonksiyon etiketi arasi

FONT = ("Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
        "'Helvetica Neue', Arial, sans-serif")

# Renkler: solda normal, sagda soluk (vurgulu varyantlarda arka plan)
FILL = {
    "v33":  ("#e8332a", "#f3b3af"),
    "v5":   ("#e8332a", "#f3b3af"),
    "gnd":  ("#3a3a3a", "#c6c6c6"),
    "gpio": ("#a8a8a8", "#e2e2e2"),
}
HI = "#25dd4a"
TAG_FILL = ("#ffe81a", "#faf3ba")
LEAD = ("#1a1a1a", "#b8b8b8")
BLUE = "#3b9bd9"


def embed(path: Path) -> str:
    return ("data:image/jpeg;base64,"
            + base64.b64encode(path.read_bytes()).decode("ascii"))


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def row_y(pin: int) -> float:
    return ROW0 + ((pin - 1) // 2) * ROW_DY


def build(variant: str) -> str:
    hl = VARIANTS[variant]
    faded = bool(hl)                       # vurgu varsa geri kalan soluklasir
    px, py, pw, ph = PANEL
    hx0 = BX + BW * HDR[0]
    hy0 = BY + BH * HDR[1]
    hx1 = BX + BW * HDR[2]
    hy1 = BY + BH * HDR[3]
    col = {1: CX - PIN_W / 2, 0: CX + PIN_W / 2}     # tek pin sol, cift pin sag

    o = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {CW:.0f} {CH:.0f}" width="{CW:.0f}" height="{CH:.0f}">\n',
        '  <title>T3 Gemstone O1 — 40-Pin Header</title>\n',
        '  <style>\n'
        f'    text {{ font-family: {FONT}; }}\n'
        '    .nm  { font-size: 27px; font-weight: 700; fill: #fff; }\n'
        '    .nmf { fill: #fdfdfd; }\n'
        '    .pn  { font-size: 30px; font-weight: 700; fill: #1a1a1a; }\n'
        '    .tag { font-size: 20px; font-weight: 700; fill: #1a1a1a;\n'
        '           stroke-width: 19px; stroke-linejoin: round;\n'
        '           paint-order: stroke fill; }\n'
        '    .box { stroke: #9a9a9a; stroke-width: 2; fill: #fff; }\n'
        '    .dash{ fill: none; stroke: ' + BLUE + '; stroke-width: 4;\n'
        '           stroke-dasharray: 16 11; }\n'
        '  </style>\n',
        f'  <rect width="{CW:.0f}" height="{CH:.0f}" fill="#fff"/>\n',
        f'  <image x="{BX:.0f}" y="{BY:.0f}" width="{BW:.0f}" height="{BH:.0f}" '
        f'xlink:href="{embed(IMG / PHOTO)}"/>\n',
        # J23 vurgusu
        f'  <rect x="{hx0:.0f}" y="{hy0:.0f}" width="{hx1-hx0:.0f}" '
        f'height="{hy1-hy0:.0f}" fill="#25dd4a" fill-opacity=".33" '
        f'stroke="#111" stroke-width="5" rx="6"/>\n',
        # J23 -> tablo oku
        f'  <path d="M {hx1+14:.0f} {(hy0+hy1)/2:.0f} L {px-46:.0f} '
        f'{(hy0+hy1)/2:.0f}" stroke="#1a1a1a" stroke-width="6" fill="none"/>\n'
        f'  <path d="M {px-18:.0f} {(hy0+hy1)/2:.0f} l -30 -17 l 0 34 z" '
        f'fill="#1a1a1a"/>\n',
    ]

    # Ust ve alt kesikli yonlendirme cizgileri (pin 1/2 ve 39/40'a).
    # Ic/dis raylar ic ice gecirildi ki iki yol birbirini kesmesin: yakin
    # sutun (pin 1) ic rayi, uzak sutun (pin 2) dis rayi kullanir.
    mid = (hx0 + hx1) / 2
    top_tip, top_base = ROW0 - 62, ROW0 - 82
    bot_tip, bot_base = row_y(40) + 41, row_y(40) + 61
    for odd, rail_t, rail_b, bx_off in ((1, 72, 1478, -24), (0, 46, 1504, 24)):
        cxp = CX - PIN_W / 2 if odd else CX + PIN_W / 2
        sx = mid + bx_off
        o.append(f'  <path class="dash" d="M {sx:.0f} {hy0:.0f} L {sx:.0f} '
                 f'{rail_t} L {cxp:.0f} {rail_t} L {cxp:.0f} {top_base:.0f}"/>\n')
        o.append(f'  <path d="M {cxp:.0f} {top_tip:.0f} l -12 -21 l 24 0 z" '
                 f'fill="{BLUE}"/>\n')
        o.append(f'  <path class="dash" d="M {sx:.0f} {hy1:.0f} L {sx:.0f} '
                 f'{rail_b} L {cxp:.0f} {rail_b} L {cxp:.0f} {bot_base:.0f}"/>\n')
        o.append(f'  <path d="M {cxp:.0f} {bot_tip:.0f} l -12 21 l 24 0 z" '
                 f'fill="{BLUE}"/>\n')

    # Panel
    o.append(f'  <rect x="{px:.0f}" y="{py:.0f}" width="{pw:.0f}" '
             f'height="{ph:.0f}" rx="26" fill="none" stroke="#ccc" '
             'stroke-width="3"/>\n')
    # PIN basligi
    o.append(f'  <rect x="{CX-PIN_W:.0f}" y="{ROW0-56:.0f}" '
             f'width="{PIN_W*2:.0f}" height="34" rx="10" '
             f'fill="{"#9a9a9a" if faded else "#3a3a3a"}"/>\n'
             f'  <text x="{CX:.0f}" y="{ROW0-32:.0f}" text-anchor="middle" '
             'font-size="21" font-weight="700" fill="#fff">PIN</text>\n')

    o.append('  <g id="pins">\n')
    for pin, kind, name, tag in PINS:
        odd = pin % 2
        y = row_y(pin)
        on = pin in hl
        if on:
            tag = hl[pin]
        dim = faded and not on

        # pin numarasi kutusu
        bx = CX - PIN_W if odd else CX
        o.append(f'    <rect class="box" x="{bx:.0f}" y="{y-PIN_H/2:.0f}" '
                 f'width="{PIN_W:.0f}" height="{PIN_H:.0f}"/>\n')
        o.append(f'    <text class="pn" x="{bx+PIN_W/2:.0f}" y="{y+11:.0f}" '
                 f'text-anchor="middle" fill="{"#8d8d8d" if dim else "#1a1a1a"}"'
                 f'>{pin}</text>\n')

        # isim hapi
        nx = (CX - PIN_W - NAME_GAP - NAME_W) if odd else (CX + PIN_W + NAME_GAP)
        fill = HI if on else FILL[kind][1 if dim else 0]
        o.append(f'    <rect x="{nx:.0f}" y="{y-NAME_H/2:.0f}" '
                 f'width="{NAME_W:.0f}" height="{NAME_H:.0f}" rx="9" '
                 f'fill="{fill}"'
                 + (' stroke="#111" stroke-width="3.5"' if on else '') + '/>\n')
        o.append(f'    <text class="nm{"f" if dim else ""}" x="{nx+NAME_W/2:.0f}"'
                 f' y="{y+10:.0f}" text-anchor="middle" '
                 f'fill="{"#1a1a1a" if on else ("#fdfdfd" if dim else "#fff")}"'
                 f'>{esc(name)}</text>\n')

        # hap ile pin kutusu arasi cizgi + nokta
        lc = LEAD[0] if on or not faded else LEAD[1]
        x0 = nx + NAME_W if odd else bx + PIN_W
        x1 = bx if odd else nx
        o.append(f'    <path d="M {x0:.0f} {y:.0f} L {x1:.0f} {y:.0f}" '
                 f'stroke="{lc}" stroke-width="{4 if on else 3}" fill="none"/>\n')
        o.append(f'    <circle cx="{x0 if odd else x1:.0f}" cy="{y:.0f}" r="5" '
                 f'fill="{lc}"/>\n')

        # fonksiyon etiketi
        if tag:
            tx = nx - TAG_GAP if odd else nx + NAME_W + TAG_GAP
            o.append(f'    <text class="tag" x="{tx:.0f}" y="{y+8:.0f}" '
                     f'text-anchor="{"end" if odd else "start"}" '
                     f'stroke="{TAG_FILL[1] if dim else TAG_FILL[0]}" '
                     f'fill="{"#8a8a80" if dim else "#1a1a1a"}"'
                     f'>{esc(tag)}</text>\n')
    o.append('  </g>\n</svg>\n')
    return "".join(o)


def main():
    if not (IMG / PHOTO).exists():
        print(f"Eksik: {IMG / PHOTO}", file=sys.stderr)
        return 1
    for v in VARIANTS:
        out = IMG / f"{v}.svg"
        out.write_text(build(v), encoding="utf-8")
        print(f"{out.relative_to(REPO)}  ({out.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
