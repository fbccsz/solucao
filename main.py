"""The World Today - an editorial picture page for Friday 13 November 2026.

Standard library only, no network, no external assets, no randomness, no
clock: two runs write byte-identical files.  Writes one 1024x1024 PNG to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
"""
import math
import os
import struct
import zlib
from pathlib import Path

W = H = 1024

PAL = {
    'paper':  'efe4cd',
    'panel':  'fbf6e8',
    'edge':   'd8c9ab',
    'ink':    '17242e',
    'night':  '15222c',
    'night2': '24404f',
    'night3': '0d1720',
    'sea':    '16303b',
    'sea2':   '20464f',
    'red':    'c0443a',
    'red2':   '8e2f28',
    'orange': 'e08334',
    'gold':   'dfa848',
    'sand':   'b08a45',
    'teal':   '16787b',
    'blue':   '3b6187',
    'slate':  '486572',
    'stone':  'b7a98c',
    'concr':  '9a9182',
    'concr2': '6d675c',
    'cream':  'fff9ea',
    'smoke':  '55636b',
    'smoke2': '7a8489',
    'grass':  '3d5b46',
}

_CC = {k: bytes.fromhex(v) for k, v in PAL.items()}


def col(n):
    return _CC[n]


pix = bytearray(col('paper') * (W * H))

CLIP = [0, 0, W, H]
ORIGIN = [0, 0]


def origin(x, y):
    ORIGIN[0], ORIGIN[1] = int(x), int(y)


def clip(x, y, w, h):
    CLIP[0], CLIP[1], CLIP[2], CLIP[3] = int(x), int(y), int(x + w), int(y + h)


def clip_off():
    CLIP[0], CLIP[1], CLIP[2], CLIP[3] = 0, 0, W, H


def rect(x, y, w, h, c):
    x, y = int(x) + ORIGIN[0], int(y) + ORIGIN[1]
    w, h = int(w), int(h)
    a = max(CLIP[0], x)
    t = max(CLIP[1], y)
    b = min(CLIP[2], x + w)
    u = min(CLIP[3], y + h)
    if b <= a or u <= t:
        return
    row = col(c) * (b - a)
    for j in range(t, u):
        pix[(j * W + a) * 3:(j * W + b) * 3] = row


def disc(cx, cy, r, c):
    cx, cy, r = int(cx), int(cy), int(r)
    if r < 0:
        return
    for j in range(-r, r + 1):
        dx = math.isqrt(max(0, r * r - j * j))
        rect(cx - dx, cy + j, 2 * dx + 1, 1, c)


def stroke(x0, y0, x1, y1, t, c):
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        disc(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n, t, c)


def poly(pts, c):
    ys = [p[1] for p in pts]
    y0, y1 = int(min(ys)), int(max(ys))
    n = len(pts)
    for y in range(y0, y1 + 1):
        sy = y + 0.5
        xs = []
        for i in range(n):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % n]
            if (ay <= sy < by) or (by <= sy < ay):
                xs.append(ax + (sy - ay) * (bx - ax) / (by - ay))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            a, b = int(round(xs[i])), int(round(xs[i + 1]))
            rect(a, y, b - a + 1, 1, c)


# 5x7 lettering, original, one hex byte per row (bit 4 = leftmost pixel).
GLYPHS = dict(zip(
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/-:.,\'!?',
    '''0E11111F111111 1E11111E11111E 0F10101010100F 1E11111111111E
    1F10101E10101F 1F10101E101010 0F10101711110F 1111111F111111
    0E04040404040E 0702020212120C 11121418141211 1010101010101F
    111B1515111111 11191513111111 0E11111111110E 1E11111E101010
    0E11111115120D 1E11111E141211 0F10100E01011E 1F040404040404
    1111111111110E 11111111110A04 11111115151B11 11110A040A1111
    11110A04040404 1F01020408101F 0E11131519110E 040C040404040E
    0E11010204081F 1E01010E01011E 02060A121F0202 1F10101E01011E
    0E10101E11110E 1F010204080808 0E11110E11110E 0E11110F01010E
    0004041F040400 01020404081010 0000001F000000 04040404040004
    00000000000004 00000000000408 04040400000000 04040400040004
    0E110102040004'''.split()))


def txt(x, y, s, k=4, c='ink', track=6):
    x = int(x)
    y = int(y)
    for ch in s.upper():
        g = GLYPHS.get(ch)
        if g is not None:
            for j in range(7):
                bits = int(g[2 * j:2 * j + 2], 16)
                for i in range(5):
                    if bits & (16 >> i):
                        rect(x + i * k, y + j * k, k, k, c)
        x += track * k
    return x


def tw(s, k=4, track=6):
    return len(s) * track * k - (track - 5) * k


def txt_c(cx, y, s, k=4, c='ink', track=6):
    txt(cx - tw(s, k, track) // 2, y, s, k, c, track)


def txt_r(xr, y, s, k=4, c='ink', track=6):
    txt(xr - tw(s, k, track), y, s, k, c, track)


# Every fitted string is recorded here so build() can prove none overflowed.
TEXT_BOXES = []


def fit(s, maxw, maxk=10, mink=3, track=6):
    """Largest k in [mink, maxk] whose rendering of s fits maxw."""
    for k in range(maxk, mink - 1, -1):
        if tw(s, k, track) <= maxw:
            return k
    raise AssertionError('%r cannot fit %dpx at k>=%d' % (s, maxw, mink))


def txt_fit(x, y, s, maxw, maxk=10, mink=3, c='ink', track=6):
    """Draw s at the largest size that fits maxw, and record its measured box."""
    k = fit(s, maxw, maxk, mink, track)
    w = tw(s, k, track)
    if w > maxw:
        raise AssertionError('%r is %dpx wide, box is %dpx' % (s, w, maxw))
    TEXT_BOXES.append((s, k, w, int(maxw)))
    return txt(x, y, s, k, c, track)


def arc(cx, cy, r, a0, a1, t, c):
    n = max(2, int(abs(a1 - a0) * r / 2))
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        disc(cx + r * math.cos(a), cy + r * math.sin(a), t, c)


def hemi(cx, cy, r, c):
    for j in range(-r, 1):
        dx = math.isqrt(max(0, r * r - j * j))
        rect(cx - dx, cy + j, 2 * dx + 1, 1, c)


def star_burst(cx, cy, r, c, spikes=8, inner=None):
    inner = inner or r // 3
    pts = []
    for i in range(spikes * 2):
        a = math.pi * 2 * i / (spikes * 2) - math.pi / 2
        rr = r if i % 2 == 0 else inner
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    poly(pts, c)


# ---------------------------------------------------------------- lead scene
def scene_gulf(w, h):
    """Iran's strike on a US early-warning radar in Bahrain, over the Gulf."""
    hz = int(h * 0.63)                       # horizon
    bands = ['night3', 'night3', 'night', 'night', 'night2']
    bh = hz / len(bands)
    for i, b in enumerate(bands):
        rect(0, i * bh, w, bh + 1, b)
    rect(0, hz, w, h - hz, 'sea')
    rect(0, hz, w, 2, 'slate')
    rect(0, hz + int((h - hz) * 0.55), w, h, 'sea2')
    # moon
    disc(w * 0.87, h * 0.17, 20, 'cream')
    disc(w * 0.87 - 8, h * 0.17 - 6, 18, 'night3')
    # sea glints
    for i, x in enumerate(range(0, w, 97)):
        rect(x + (i * 37) % 53, hz + 14 + (i * 23) % 60, 60 + (i * 41) % 70, 3,
             'sea2' if i % 2 else 'slate')

    dx, dy = int(w * 0.27), hz             # radar dome centre on the horizon
    # platform
    rect(dx - 74, dy - 3, 148, 16, 'concr2')
    for i in range(5):
        rect(dx - 60 + i * 30, dy + 13, 8, 26, 'concr2')
    # radar arcs
    for r in (86, 118, 150):
        arc(dx, dy - 20, r, -math.pi * 0.92, -math.pi * 0.18, 2, 'teal')
    # dome
    hemi(dx, dy - 4, 66, 'stone')
    hemi(dx, dy - 4, 62, 'cream')
    for a in (-1.35, -1.05, -0.75, -0.45, -0.15):
        stroke(dx + 58 * math.cos(a), dy - 4 + 58 * math.sin(a) * 0.98,
               dx, dy - 4, 2, 'slate')
    arc(dx, dy - 4, 40, -math.pi, 0, 2, 'slate')
    arc(dx, dy - 4, 20, -math.pi, 0, 2, 'slate')
    # damaged wedge
    poly([(dx + 8, dy - 60), (dx + 62, dy - 26), (dx + 46, dy - 4),
          (dx + 12, dy - 12)], 'night3')
    poly([(dx + 12, dy - 58), (dx + 60, dy - 26), (dx + 44, dy - 6),
          (dx + 14, dy - 14)], 'red')
    # impact flash
    star_burst(dx + 54, dy - 30, 46, 'orange', 9, 12)
    star_burst(dx + 54, dy - 30, 26, 'gold', 7, 7)
    star_burst(dx + 54, dy - 30, 12, 'cream', 6, 4)
    # incoming missile trail
    mx, my = int(w * 0.06), int(h * 0.10)
    for i in range(16):
        f = i / 15
        x = mx + (dx + 54 - mx) * f
        y = my + (dy - 30 - my) * f
        r = 3 + int(9 * (1 - f))
        disc(x - 8, y - 6, r, 'smoke')
        disc(x - 10, y - 7, max(1, r - 4), 'smoke2')
    stroke(mx, my, dx + 54, dy - 30, 4, 'red')
    stroke(mx, my, dx + 54, dy - 30, 2, 'gold')
    poly([(mx - 8, my - 6), (mx + 16, my + 6), (mx - 4, my + 14)], 'gold')
    # distant shipping along the horizon
    for x, s in ((int(w * 0.62), 1), (int(w * 0.70), 0), (int(w * 0.78), 1)):
        c = 'slate' if s else 'smoke'
        rect(x, hz - 12, 54, 10, c)
        rect(x + 14, hz - 22, 22, 12, c)
        rect(x + 20, hz - 30, 8, 10, c)
    # a listing tanker, deeper water
    poly([(w - 210, hz + 46), (w - 40, hz + 28), (w - 34, hz + 62),
          (w - 196, hz + 82)], 'stone')
    poly([(w - 210, hz + 46), (w - 40, hz + 28), (w - 40, hz + 36),
          (w - 208, hz + 54)], 'concr2')
    rect(w - 176, hz + 18, 40, 22, 'cream')
    rect(w - 132, hz + 24, 10, 34, 'red')
    for i in range(9):
        x = w - 300 + i * 34
        rect(x, hz + 90 + (i % 3) * 12, 46, 3, 'slate')


# --------------------------------------------------------------- panel scenes
def scene_talks(w, h):
    """Three-flag negotiating table."""
    rect(0, 0, w, h, 'sand')
    rect(0, int(h * 0.52), w, h, 'stone')
    rect(0, int(h * 0.52), w, 4, 'gold')
    # window light
    rect(w * 0.06, h * 0.10, w * 0.30, h * 0.36, 'cream')
    rect(w * 0.06 + 6, h * 0.10 + 6, w * 0.30 - 12, h * 0.36 - 12, 'gold')
    # flags
    flags = [('blue', 'gold'), ('red', 'cream'), ('blue', 'gold')]
    for i, (top, bot) in enumerate(flags):
        fx = int(w * (0.30 + i * 0.20))
        stroke(fx, int(h * 0.18), fx, int(h * 0.62), 3, 'ink')
        rect(fx, int(h * 0.18), 44, 30, top)
        rect(fx, int(h * 0.18) + 30, 44, 16, bot)
        if i == 1:                                  # stripes + canton
            for s in range(3):
                rect(fx, int(h * 0.18) + 30 + s * 8, 44, 4, 'red')
            rect(fx, int(h * 0.18), 20, 18, 'blue')
    # table
    poly([(w * 0.10, h * 1.02), (w * 0.20, h * 0.64),
          (w * 0.80, h * 0.64), (w * 0.90, h * 1.02)], 'ink')
    poly([(w * 0.10, h * 1.02), (w * 0.20, h * 0.64),
          (w * 0.80, h * 0.64), (w * 0.90, h * 1.02)], 'night')
    poly([(w * 0.20, h * 0.64), (w * 0.80, h * 0.64),
          (w * 0.79, h * 0.72), (w * 0.21, h * 0.72)], 'concr2')
    # two chairs, seen from behind
    for cx in (w * 0.30, w * 0.70):
        rect(cx - 34, h * 0.80, 68, 40, 'red2')
        rect(cx - 24, h * 0.74, 48, 24, 'red')


def scene_chip(w, h):
    """Microchip and a falling line."""
    rect(0, 0, w, h, 'night3')
    rect(0, 0, w, h * 0.5, 'night')
    # grid
    for x in range(0, w, 24):
        rect(x, 0, 1, h, 'night2')
    for y in range(0, h, 24):
        rect(0, y, w, 1, 'night2')
    # chip
    cx, cy, s = w * 0.38, h * 0.50, 46
    rect(cx - s, cy - s, 2 * s, 2 * s, 'teal')
    rect(cx - s + 6, cy - s + 6, 2 * s - 12, 2 * s - 12, 'night')
    rect(cx - 24, cy - 24, 48, 48, 'slate')
    rect(cx - 14, cy - 14, 28, 28, 'teal')
    for i in range(4):
        o = -30 + i * 20
        rect(cx + o, cy - s - 10, 8, 10, 'stone')
        rect(cx + o, cy + s, 8, 10, 'stone')
        rect(cx - s - 10, cy + o, 10, 8, 'stone')
        rect(cx + s, cy + o, 10, 8, 'stone')
    # falling line
    pts = [(w * 0.10, h * 0.20), (w * 0.30, h * 0.30), (w * 0.46, h * 0.26),
           (w * 0.62, h * 0.52), (w * 0.78, h * 0.86), (w * 0.90, h * 0.80)]
    for i in range(len(pts) - 1):
        stroke(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], 5, 'red')
    stroke(pts[1][0], pts[1][1], pts[2][0], pts[2][1], 5, 'gold')
    disc(pts[-1][0], pts[-1][1], 9, 'red')
    poly([(pts[-1][0] - 20, pts[-1][1] - 4), (pts[-1][0] + 4, pts[-1][1] - 4),
          (pts[-1][0] - 8, pts[-1][1] + 34)], 'red')


def scene_bus(w, h):
    """Bus on its side, wrecked truck ahead."""
    rect(0, 0, w, h, 'sky' if 'sky' in _CC else 'stone')
    rect(0, 0, w, h * 0.58, 'gold')
    rect(0, h * 0.58, w, h, 'smoke2')
    rect(0, h * 0.58, w, 6, 'concr2')
    rect(0, h * 0.74, w, h, 'slate')
    for i in range(6):
        rect(w * 0.04 + i * w * 0.16, h * 0.80, w * 0.09, 6, 'cream')
    # bus on its side
    bx, by = w * 0.34, h * 0.66
    poly([(bx - 120, by), (bx + 96, by - 46), (bx + 106, by - 6),
          (bx - 116, by + 40)], 'orange')
    poly([(bx - 120, by), (bx + 96, by - 46), (bx + 98, by - 34),
          (bx - 118, by + 12)], 'cream')
    for i in range(5):
        x = bx - 98 + i * 38
        poly([(x, by + 8), (x + 26, by), (x + 28, by - 14), (x + 2, by - 6)], 'night')
    for dx in (-70, 40):
        disc(bx + dx, by + 26, 16, 'ink')
        disc(bx + dx, by + 26, 6, 'concr2')
    rect(bx + 96, by - 40, 18, 34, 'red')
    # truck cab
    tx = w * 0.80
    poly([(tx - 20, h * 0.68), (tx + 62, h * 0.62), (tx + 66, h * 0.80),
          (tx - 18, h * 0.84)], 'red')
    rect(tx + 4, h * 0.65, 34, 16, 'cream')
    disc(tx + 12, h * 0.82, 14, 'ink')
    disc(tx + 52, h * 0.80, 14, 'ink')
    # dust
    for i, (x, y, r) in enumerate(((w * 0.08, h * 0.52, 26), (w * 0.58, h * 0.44, 20),
                                   (w * 0.92, h * 0.44, 22))):
        disc(x, y, r, 'smoke2' if i % 2 else 'stone')
    # skid marks
    for i in range(3):
        stroke(w * 0.06 + i * 14, h * 0.96, w * 0.46 + i * 18, h * 0.80, 2, 'ink')


def scene_rubble(w, h):
    """Collapsed building, rescue crane."""
    rect(0, 0, w, h, 'stone')
    rect(0, 0, w, h * 0.44, 'night2')
    rect(0, h * 0.44, w, h, 'sand')
    rect(0, h * 0.44, w, 5, 'gold')
    # standing remnant of the building
    rect(w * 0.06, h * 0.10, w * 0.26, h * 0.44, 'concr')
    for i in range(3):
        rect(w * 0.10 + i * w * 0.07, h * 0.16, w * 0.04, h * 0.10, 'night3')
    rect(w * 0.06, h * 0.10, w * 0.26, 8, 'concr2')
    # tilted slab
    poly([(w * 0.20, h * 0.52), (w * 0.62, h * 0.24), (w * 0.70, h * 0.40),
          (w * 0.28, h * 0.68)], 'concr')
    poly([(w * 0.20, h * 0.52), (w * 0.62, h * 0.24), (w * 0.63, h * 0.30),
          (w * 0.21, h * 0.58)], 'cream')
    for i in range(6):
        x = w * 0.26 + i * w * 0.07
        stroke(x, h * 0.52 - i * 3, x + 10, h * 0.30 - i * 3, 1, 'ink')
    # rubble
    poly([(0, h), (0, h * 0.72), (w * 0.16, h * 0.80), (w * 0.34, h * 0.70),
          (w * 0.52, h * 0.86), (w * 0.70, h), ], 'concr2')
    for i, (x, y, s) in enumerate(((w * 0.10, h * 0.78, 18), (w * 0.30, h * 0.72, 14),
                                   (w * 0.50, h * 0.82, 20))):
        poly([(x, y - s), (x + s, y + s), (x - s, y + s)], 'stone')
    # crane on the right
    stroke(w * 0.86, h * 1.0, w * 0.86, h * 0.06, 6, 'gold')
    stroke(w * 0.86, h * 0.06, w * 0.52, h * 0.12, 6, 'gold')
    for i in range(8):
        f = i / 7.0
        x = w * 0.86 + (w * 0.52 - w * 0.86) * f
        y = h * 0.06 + (h * 0.12 - h * 0.06) * f
        stroke(x, y, x + 12, y + 18, 1, 'sand')
    stroke(w * 0.62, h * 0.10, w * 0.62, h * 0.46, 2, 'ink')
    rect(w * 0.62 - 9, h * 0.46, 18, 12, 'red')
    # dust
    for i, (x, y, r) in enumerate(((w * 0.42, h * 0.66, 24), (w * 0.72, h * 0.74, 18))):
        disc(x, y, r, 'smoke2')


# ------------------------------------------------------------------- layout
# Vertical budget: masthead 136 | lead 268 | gap 16 | 2 rows of 266 | footer 56.
LEAD = (24, 136, 976, 268)
LEAD_ART_H = 140
MAST_H = 136
PANEL_W = (W - 3 * 24) // 2
PANEL_H = 266
PANEL_ART_H = 132
ROW1_Y = 420
FOOTER_H = 56

STORIES = [
    # (scene, accent, kicker, line1, line2)
    (scene_talks, 'blue', 'UKRAINE / TALKS', 'ZELENSKY', 'MEETS ENVOYS'),
    (scene_chip, 'teal', 'TECH / MARKETS', 'NVIDIA', 'CHIEF QUITS'),
    (scene_bus, 'red', 'ASSAM / INDIA', 'BUS CRASH', '26 KILLED'),
    (scene_rubble, 'gold', 'NAIROBI / KENYA', 'BUILDING', 'COLLAPSE'),
]


def masthead():
    rect(0, 0, W, MAST_H, 'ink')
    rect(0, MAST_H - 5, W, 5, 'gold')
    rect(24, 10, W - 48, 2, 'night2')
    txt(24, 18, 'FRIDAY 13 NOVEMBER 2026', 3, 'gold')
    txt_r(W - 24, 18, 'ILLUSTRATED SUMMARY', 3, 'stone')
    txt_c(W // 2, 44, 'THE WORLD TODAY', 10, 'cream')
    rect(W // 2 - 60, 122, 120, 4, 'red')


def lead_block():
    x, y, w, h = LEAD
    cap_h = h - LEAD_ART_H
    cap_y = y + LEAD_ART_H
    # art
    rect(x, y, w, LEAD_ART_H, 'night')
    clip(x, y, w, LEAD_ART_H)
    origin(x, y)
    scene_gulf(w, LEAD_ART_H)
    origin(0, 0)
    clip_off()
    # caption strip, inside the block: dark, so nothing sits on the paper
    rect(x, cap_y, w, cap_h, 'night')
    rect(x, cap_y, w, 3, 'red')
    rect(x, cap_y + 3, 9, cap_h - 3, 'red')
    rect(x, cap_y + cap_h - 1, w, 1, 'ink')

    txt_fit(x + 30, cap_y + 10, 'BAHRAIN / GULF', w - 60, 3, 3, 'gold')

    mw = w - 60 - 330                     # headline column
    k1 = fit('IRAN SAYS IT HIT', mw)
    k2 = fit('A US RADAR', mw)
    k = min(k1, k2, 6)
    txt_fit(x + 30, cap_y + 34, 'IRAN SAYS IT HIT', mw, k, 4, 'cream')
    txt_fit(x + 30, cap_y + 34 + k * 7 + 6, 'A US RADAR', mw, k, 4, 'cream')

    rx = x + w - 30
    txt_r(rx, cap_y + 42, 'SHIPPING ON ALERT', 3, 'stone')
    txt_r(rx, cap_y + 68, 'A RETALIATION', 3, 'stone')
    txt_r(rx, cap_y + 94, 'GULF ON EDGE', 3, 'slate')


def panel(i, sx, sy, pw, ph):
    fn, accent, kicker, l1, l2 = STORIES[i]
    cap_y = sy + PANEL_ART_H
    cap_h = ph - PANEL_ART_H
    rect(sx, sy, pw, ph, 'ink')
    clip(sx, sy, pw, PANEL_ART_H)
    origin(sx, sy)
    fn(pw, PANEL_ART_H)
    origin(0, 0)
    clip_off()
    # accent rule and kicker strip, then the headline strip: no overlaps
    rect(sx, cap_y, pw, 4, accent)
    rect(sx, cap_y + 4, pw, cap_h - 4, 'night')
    rect(sx + 14, cap_y + 16, 5, cap_h - 30, accent)
    txt_fit(sx + 30, cap_y + 10, kicker, pw - 52, 3, 3, accent)
    mw = pw - 56
    k = min(fit(l1, mw), fit(l2, mw), 6)
    ty = cap_y + 34
    txt_fit(sx + 30, ty, l1, mw, k, 4, 'cream')
    txt_fit(sx + 30, ty + k * 7 + 6, l2, mw, k, 4, 'cream')


def footer():
    rect(0, H - FOOTER_H, W, FOOTER_H, 'ink')
    rect(0, H - FOOTER_H, W, 3, 'night2')
    txt(24, H - 42, 'ILLUSTRATED SUMMARY OF REPORTED NEWS', 3, 'stone')
    txt_r(W - 24, H - 42, 'NOT A PHOTOGRAPH', 3, 'stone')


def build():
    masthead()
    lead_block()
    for i in range(4):
        sx = 24 + (i % 2) * (PANEL_W + 24)
        sy = ROW1_Y + (i // 2) * (PANEL_H + 16)
        panel(i, sx, sy, PANEL_W, PANEL_H)
    footer()
    # every fitted string has already been measured; this proves the set is clean
    for s, k, w, box in TEXT_BOXES:
        assert w <= box, (s, k, w, box)


build()

# --------------------------------------------------------------------- write
def chunk(tag, data):
    return (struct.pack('>I', len(data)) + tag + data
            + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))


raw = b''.join(b'\x00' + bytes(pix[i:i + W * 3]) for i in range(0, len(pix), W * 3))
png = (b'\x89PNG\r\n\x1a\n'
       + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
       + chunk(b'IDAT', zlib.compress(raw, 9))
       + chunk(b'IEND', b''))
assert len(png) <= 1048576, len(png)
out = Path(os.environ.get('MAKEFUN_OUTPUT_DIR', '/output'))
out.mkdir(parents=True, exist_ok=True)
(out / 'entry.png').write_bytes(png)
print('wrote', out / 'entry.png', len(png), 'bytes')
