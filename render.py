#!/usr/bin/env python3
"""Draw "THE WORLD TODAY" — a newspaper front page summing up
Wednesday 25 November 2026. All art is drawn in code with PIL.
Outputs entry.png (1024x1024, <= 1 MiB) next to this script."""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 243, 232)
INK = (26, 26, 26)
RED = (176, 42, 30)
BLUE = (31, 78, 121)
GOLD = (180, 138, 20)
GREY = (96, 92, 84)
LIGHT = (226, 219, 205)
ORANGE = (214, 110, 30)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, max_w):
    """Greedy word wrap returning lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, fnt, max_w, leading, color=INK):
    for line in wrap(d, text, fnt, max_w):
        d.text((x, y), line, font=fnt, fill=color)
        y += leading
    return y


def rule(d, x0, y, x1, width=2, color=INK):
    d.line([(x0, y), (x1, y)], fill=color, width=width)


def headline(d, x, y, lines, size, color=INK, leading=None):
    f = font(SERIF_B, size)
    leading = leading or int(size * 1.12)
    for line in lines:
        d.text((x, y), line, font=f, fill=color)
        y += leading
    return y


def kicker(d, x, y, text, color=RED, size=19):
    f = font(SANS_B, size)
    d.text((x, y), text, font=f, fill=color)
    return y + size + 8


def draw_bars(d, x, y, w, rows):
    """rows: (label, pct) — horizontal bars, pct of 20 max."""
    f_lab = font(SANS_B, 17)
    f_val = font(SANS_B, 17)
    title = font(SANS_B, 16)
    d.text((x, y), "CAPPED TARIFF RATES", font=title, fill=GREY)
    y += 26
    for label, pct in rows:
        d.text((x, y), label, font=f_lab, fill=INK)
        bx = x + 118
        bw = int((w - 118 - 52) * pct / 20.0)
        d.rectangle([bx, y + 2, bx + bw, y + 16], fill=RED)
        d.text((bx + bw + 6, y), f"{pct}%", font=f_val, fill=RED)
        y += 30
    return y


def draw_kospi_chart(d, x, y, w, h):
    """Descending line chart with red dots."""
    d.rectangle([x, y, x + w, y + h], outline=GREY, width=1)
    pts = [(0, 0.12), (0.2, 0.28), (0.4, 0.30), (0.6, 0.55), (0.8, 0.72), (1.0, 0.92)]
    coords = [(x + 8 + p * (w - 16), y + 8 + v * (h - 16)) for p, v in pts]
    d.line(coords, fill=RED, width=3)
    for cx, cy in coords:
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED)
    f = font(SANS_B, 15)
    d.text((x + 8, y + h + 6), "MON", font=f, fill=GREY)
    d.text((x + w - 38, y + h + 6), "WED", font=f, fill=GREY)
    return y + h + 24


def draw_rocket(d, x, y, s):
    """Small rocket + station, scaled by s."""
    # station: horizontal module with panels
    d.rectangle([x, y + 8, x + 150 * s, y + 22 * s], fill=BLUE)
    d.rectangle([x + 14 * s, y, x + 136 * s, y + 8 * s], fill=(120, 150, 185))
    d.rectangle([x + 60 * s, y + 22 * s, x + 90 * s, y + 34 * s], fill=(210, 220, 235))
    # rocket body
    rx, ry = x + 170 * s, y + 60 * s
    d.polygon([(rx, ry - 46 * s), (rx + 14 * s, ry - 22 * s),
               (rx + 14 * s, ry + 26 * s), (rx - 14 * s, ry + 26 * s),
               (rx - 14 * s, ry - 22 * s)], fill=(235, 235, 235),
              outline=INK)
    d.ellipse([rx - 7 * s, ry - 12 * s, rx + 7 * s, ry + 2 * s],
              fill=BLUE)
    d.polygon([(rx - 14 * s, ry + 26 * s), (rx - 26 * s, ry + 42 * s),
               (rx - 14 * s, ry + 34 * s)], fill=RED)
    d.polygon([(rx + 14 * s, ry + 26 * s), (rx + 26 * s, ry + 42 * s),
               (rx + 14 * s, ry + 34 * s)], fill=RED)
    d.polygon([(rx - 6 * s, ry + 26 * s), (rx + 6 * s, ry + 26 * s),
               (rx, ry + 48 * s)], fill=ORANGE)
    # stars
    for sx, sy in [(x + 8, y + 44), (x + 200, y + 6), (x + 216, y + 44),
                   (x + 30, y + 70), (x + 190, y + 78)]:
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=GOLD)


def draw_bolt(d, x, y, s):
    d.polygon([(x + 12 * s, y), (x + 26 * s, y), (x + 16 * s, y + 16 * s),
               (x + 24 * s, y + 16 * s), (x + 8 * s, y + 34 * s),
               (x + 14 * s, y + 15 * s), (x + 6 * s, y + 15 * s)],
              fill=GOLD)


def draw_flame(d, x, y, s):
    d.polygon([(x + 14 * s, y), (x + 22 * s, y + 10 * s),
               (x + 28 * s, y + 8 * s), (x + 26 * s, y + 22 * s),
               (x + 18 * s, y + 34 * s), (x + 6 * s, y + 26 * s),
               (x + 4 * s, y + 12 * s)], fill=ORANGE)
    d.polygon([(x + 14 * s, y + 18 * s), (x + 20 * s, y + 24 * s),
               (x + 14 * s, y + 32 * s), (x + 9 * s, y + 25 * s)],
              fill=(255, 200, 60))


def draw_drop(d, x, y, s):
    d.polygon([(x + 14 * s, y), (x + 26 * s, y + 20 * s),
               (x + 2 * s, y + 20 * s)], fill=BLUE)
    d.ellipse([x + 2 * s, y + 14 * s, x + 26 * s, y + 34 * s], fill=BLUE)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 36                      # margin
    RX = W - MX                  # right edge

    # ---- Masthead ----
    f_mast = font(SERIF_B, 66)
    title = "THE WORLD TODAY"
    tw = d.textlength(title, font=f_mast)
    d.text(((W - tw) / 2, 22), title, font=f_mast, fill=INK)
    rule(d, MX, 104, RX, 3)
    rule(d, MX, 110, RX, 1)

    # ---- Date band ----
    d.rectangle([MX, 120, RX, 158], fill=INK)
    f_date = font(SANS_B, 24)
    date_txt = "WEDNESDAY, 25 NOVEMBER 2026"
    dw = d.textlength(date_txt, font=f_date)
    d.text(((W - dw) / 2, 128), date_txt, font=f_date, fill=PAPER)

    # ---- Lead story: US tariffs ----
    y = 178
    y = kicker(d, MX, y, "TRADE  •  WASHINGTON")
    y = headline(d, MX, y, ["TRUMP UNVEILS NEW", "TARIFFS ON 14 ECONOMIES"], 40)
    y += 4
    y = para(d, MX, y,
             "China capped at 20% as the U.S. rebuilds duties "
             "struck down by the Supreme Court. Hearings from January.",
             font(SANS, 19), 640, 25, color=(60, 58, 52))
    # bar chart, right of the lead
    draw_bars(d, 712, 190, RX - 712,
              [("China", 20), ("SE Asia", 18), ("EU & allies", 15),
               ("Singapore", 10)])
    rule(d, MX, 372, RX, 2)

    # ---- Two columns: Kospi + Shenzhou ----
    col_y = 392
    # left: markets
    y = kicker(d, MX, col_y, "MARKETS  •  SEOUL")
    y = headline(d, MX, y, ["AI DOUBTS SINK", "ASIAN CHIP STOCKS"], 29)
    y += 2
    y = para(d, MX, y,
             "Kospi −6.2% to 4,697, its lowest since January. "
             "Samsung −9.9%, SK Hynix −11.1%, SoftBank −14.8%.",
             font(SANS, 18), 448, 24, color=(60, 58, 52))
    y += 8
    draw_kospi_chart(d, MX, y, 448, 92)
    # divider
    d.line([(512, 392), (512, 668)], fill=LIGHT, width=2)
    # right: space
    y = kicker(d, 536, col_y, "SPACE  •  TIANGONG", color=BLUE)
    y = headline(d, 536, y, ["PAKISTAN'S FIRST", "ASTRONAUT DOCKS", "AT TIANGONG"], 29)
    y += 2
    y = para(d, 536, y,
             "Shenzhou-24 crew enters China's station. "
             "Zeeshan Ali is the first foreign visitor.",
             font(SANS, 18), 452, 24, color=(60, 58, 52))
    y += 6
    draw_rocket(d, 600, y + 6, 1.0)
    rule(d, MX, 690, RX, 2)

    # ---- Bottom briefs: three columns ----
    by = 710
    cols = [
        ("UK ENERGY CAP +26%", "Typical bill £1,723 → £2,166 a year from January.",
         draw_bolt),
        ("CAIRO TANKER FIRE", "At least 30 killed on the Ring Road; dozens of cars charred.",
         draw_flame),
        ("JAVA MINE FLOOD", "9 dead, 17 trapped in a flooded Bogor gold shaft.",
         draw_drop),
    ]
    cw = 300
    for i, (head, body, icon) in enumerate(cols):
        x = MX + i * (cw + 12)
        icon(d, x, by + 2, 1.0)
        hf = font(SANS_B, 19)
        d.text((x + 36, by + 4), head, font=hf, fill=RED)
        para(d, x, by + 34, body, font(SANS, 17), cw, 22,
             color=(60, 58, 52))
        if i < 2:
            d.line([(x + cw + 6, by), (x + cw + 6, by + 130)],
                   fill=LIGHT, width=2)

    # ---- Also today strip ----
    rule(d, MX, 848, RX, 1, color=GREY)
    f_also = font(SANS_B, 16)
    d.text((MX, 860), "ALSO TODAY", font=f_also, fill=RED)
    f_item = font(SANS, 17)
    also = [
        "Nvidia −5.9% a day after soaring 31.5% on Jensen Huang's return as CEO.",
        "Anthropic sinks 6.5%, closing below its $83 IPO price.",
        "Wall Street ends lower as the AI pullback loses momentum late in the day.",
    ]
    ay = 884
    for item in also:
        d.text((MX + 24, ay), "•  " + item, font=f_item, fill=(60, 58, 52))
        ay += 25

    # ---- Footer ----
    rule(d, MX, 962, RX, 2)
    f_foot = font(SANS_B, 16)
    foot = "THE WORLD TODAY  •  WEDNESDAY 25 NOVEMBER 2026  •  THE DAY IN BRIEF"
    fw = d.textlength(foot, font=f_foot)
    d.text(((W - fw) / 2, 976), foot, font=f_foot, fill=GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print(out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
