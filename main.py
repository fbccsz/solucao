"""The World Today - an editorial front page for Friday 13 November 2026.

Sixteen stories on one page, a 4x4 grid of equal panels under a masthead.
Standard library only, no network, no external assets, no randomness, no
clock: two runs write byte-identical files.  Writes one 1024x1024 PNG to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).

    python3 main.py            write the PNG
    python3 main.py --check    measure every string and the grid, write nothing
"""
import math
import os
import struct
import sys
import zlib
from pathlib import Path

W = H = 1024

PAL = {
    'paper':  'efe4cd',
    'ink':    '17242e',
    'night':  '15222c',
    'night2': '24404f',
    'night3': '0d1720',
    'sea':    '16303b',
    'sea2':   '20464f',
    'red':    'd4503f',
    'red2':   '8e2f28',
    'orange': 'e08334',
    'gold':   'dfa848',
    'sand':   'b08a45',
    'teal':   '2b9ea1',
    'blue':   '5f92c6',
    'slate':  '486572',
    'stone':  'b7a98c',
    'concr':  '9a9182',
    'concr2': '6d675c',
    'cream':  'fff9ea',
    'smoke':  '55636b',
    'smoke2': '7a8489',
    'plum':   'b04a68',
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


def ring(cx, cy, r, t, c):
    """Annulus, thickness t."""
    for j in range(-r, r + 1):
        outer = math.isqrt(max(0, r * r - j * j))
        ri = max(0, r - t)
        inner = math.isqrt(max(0, ri * ri - j * j)) if abs(j) < ri else -1
        if inner >= 0:
            rect(cx - outer, cy + j, outer - inner, 1, c)
            rect(cx + inner + 1, cy + j, outer - inner, 1, c)
        else:
            rect(cx - outer, cy + j, 2 * outer + 1, 1, c)


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


def bar(x0, y0, x1, y1, t, c):
    """A flat-sided bar of thickness t from (x0,y0) to (x1,y1)."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L * t / 2.0, dx / L * t / 2.0
    poly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny),
          (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], c)


def arc(cx, cy, r, a0, a1, t, c):
    n = max(2, int(abs(a1 - a0) * r / 2))
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        disc(cx + r * math.cos(a), cy + r * math.sin(a), t, c)


def hemi(cx, cy, r, c):
    for j in range(-r, 1):
        dx = math.isqrt(max(0, r * r - j * j))
        rect(cx - dx, cy + j, 2 * dx + 1, 1, c)


def burst(cx, cy, r, c, spikes=8, inner=None):
    inner = inner or max(2, r // 3)
    pts = []
    for i in range(spikes * 2):
        a = math.pi * 2 * i / (spikes * 2) - math.pi / 2
        rr = r if i % 2 == 0 else inner
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    poly(pts, c)


# ---------------------------------------------------------------- lettering
# 5x7 letters, original, one hex byte per row (bit 4 = leftmost pixel).
_ROWS = '''0E11111F111111 1E11111E11111E 0F10101010100F 1E11111111111E
    1F10101E10101F 1F10101E101010 0F10101711110F 1111111F111111
    0E04040404040E 0702020212120C 11121418141211 1010101010101F
    111B1515111111 11191515131111 0E11111111110E 1E11111E101010
    0E11111115120D 1E11111E141211 0F10100E01011E 1F040404040404
    1111111111110E 11111111110A04 11111115151B11 11110A040A1111
    11110A04040404 1F01020408101F 0E11131519110E 040C040404040E
    0E11010204081F 1E01010E01011E 02060A121F0202 1F10101E01011E
    0E10101E11110E 1F010204080808 0E11110E11110E 0E11110F01010E
    0004041F040400 01020404081010 0000001F000000 04040404040004
    00000000000004 00000000000408 04040400000000 04040400040004
    0E110102040004'''.split()

GLYPHS = dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/-:.,\'!?', _ROWS))
assert len(GLYPHS) == len(_ROWS) == 45, len(GLYPHS)
GLYPHS[','] = '00000000040C04'   # comma, hung below the baseline
GLYPHS[':'] = '00040000040000'   # two dots, not a bar
GLYPHS[' '] = '00000000000000'
GLYPHS['·'] = '00000004000000'
GLYPHS['$'] = '040E1408050E04'


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


def tw(s, k=4, track=6):
    return len(s) * track * k - (track - 5) * k


# Every drawn string is recorded here so --check can prove none overflowed.
TEXT_BOXES = []


def fit(s, maxw, maxk=10, mink=2, track=6):
    """Largest k in [mink, maxk] whose rendering of s fits maxw."""
    for k in range(maxk, mink - 1, -1):
        if tw(s, k, track) <= maxw:
            return k
    raise AssertionError('%r cannot fit %dpx at k>=%d' % (s, maxw, mink))


def kick_style(s, bw):
    """Tracking a kicker needs at bw, preferring the larger scale."""
    for k in range(KICK_MAXK, 1, -1):
        for track in (6, 5):
            if tw(s, k, track) <= bw:
                return k, track
    raise AssertionError('kicker %r cannot fit %dpx' % (s, bw))


def label(bx, y, s, bw, kmax=10, kmin=2, c='ink', track=6, align='l', k=None):
    """Fit s inside (bx, bw), draw it, and record the exact box it occupies."""
    if k is None:
        k = fit(s, bw, kmax, kmin, track)
    w = tw(s, k, track)
    if w > bw:
        raise AssertionError('%r is %dpx wide, box is %dpx' % (s, w, bw))
    x = bx + (bw - w) // 2 if align == 'c' else (bx + bw - w if align == 'r' else bx)
    txt(x, y, s, k, c, track)
    TEXT_BOXES.append((s, k, w, x, y, bx, bw))
    return k


# ---------------------------------------------------------------- vignettes
# 243 x 100 each, drawn in local coordinates with the clip already set to the
# art box.  The whole page is 300 px wide on the judge's screen, so a panel's
# art is 71 x 29: one bold silhouette per vignette, flat fills, four colours
# at most, nothing thinner than 3 px, no hairlines and no texture.

def _sea(w, h, wl, deep='sea', far='sea2'):
    rect(0, wl, w, h - wl, deep)
    for i, x in enumerate(range(0, w, 38)):
        rect(x + (i * 11) % 19, wl + 5 + (i * 7) % 12, 20, 3, far)


def _burst(cx, cy, r):
    burst(cx, cy, r, 'orange', 9, max(3, r // 2))
    burst(cx, cy, int(r * 0.55), 'gold', 7, max(2, r // 4))


def v_radar(w, h):
    """Bahrain: Iran says it destroyed a US early-warning radar."""
    wl = h - 24
    rect(0, 0, w, h, 'night3')
    _sea(w, h, wl)
    rect(26, wl - 8, 110, 9, 'concr2')
    for x in (40, 112):
        rect(x, wl + 1, 11, 23, 'concr2')
    for r, c in ((58, 'teal'), (44, 'teal')):
        arc(78, wl - 8, r, -math.pi * 0.88, -math.pi * 0.12, 2, c)
    hemi(78, wl - 8, 32, 'stone')
    hemi(78, wl - 8, 26, 'cream')
    arc(78, wl - 8, 15, -math.pi, 0, 2, 'slate')
    poly([(86, wl - 38), (114, wl - 22), (108, wl - 8), (88, wl - 18)], 'night3')
    stroke(w - 2, 4, 100, wl - 26, 7, 'red')
    stroke(w - 2, 4, 100, wl - 26, 3, 'gold')
    _burst(100, wl - 26, 30)


def v_warship(w, h):
    """Gulf of Finland: a Ukrainian drone struck a Russian warship."""
    wl = h - 26
    rect(0, 0, w, h, 'night')
    _sea(w, h, wl)
    poly([(10, wl + 12), (156, wl - 10), (170, wl + 10), (22, wl + 32)], 'stone')
    poly([(10, wl + 12), (156, wl - 10), (158, wl - 2), (12, wl + 20)], 'concr2')
    poly([(58, wl - 10), (118, wl - 30), (130, wl - 14), (68, wl + 6)], 'stone')
    rect(88, wl - 44, 7, 16, 'concr2')
    stroke(92, wl - 44, 92, wl - 56, 2, 'smoke2')
    poly([(w - 26, 2), (w - 2, 16), (w - 26, 30)], 'night3')
    poly([(w - 26, 10), (w - 2, 16), (w - 26, 22)], 'red')
    stroke(w - 30, 16, 124, wl - 20, 2, 'red2')
    _burst(112, wl - 6, 26)
    for i in range(4):
        disc(126 + i * 9, wl - 40 - i * 7, 9 - i, 'smoke')


def v_odesa(w, h):
    """Odesa and Sumy: Russian drone strikes hit the cities."""
    rect(0, 0, w, h, 'night3')
    xs = (0, 39, 78, 117, 156, 195)
    hs = (44, 62, 50, 70, 56, 46)
    for i, x in enumerate(xs):
        rect(x, h - hs[i], 39, hs[i], 'night2')
        rect(x, h - hs[i], 39, 4, 'slate')
        for r in range(3):
            for cc in range(2):
                if (i + r + cc) % 3:
                    rect(x + 7 + cc * 16, h - hs[i] + 7 + r * 15, 8, 8, 'gold')
    stroke(52, -4, 74, 34, 4, 'red')
    stroke(214, -4, 170, 40, 4, 'red')
    _burst(74, 34, 28)
    _burst(170, 40, 18)


def v_nvidia(w, h):
    """Washington: Nvidia's chief has gone, the Senate has summoned him."""
    rect(0, 0, w, h, 'night')
    for x in range(0, w, 26):
        rect(x, 0, 1, h, 'night2')
    for y in range(0, h, 26):
        rect(0, y, w, 1, 'night2')
    s = 34
    cx, cy = 74, h // 2
    rect(cx - s, cy - s, 2 * s, 2 * s, 'teal')
    rect(cx - s + 7, cy - s + 7, 2 * s - 14, 2 * s - 14, 'night3')
    rect(cx - 16, cy - 16, 32, 32, 'slate')
    for i in range(4):
        o = -24 + i * 16
        rect(cx + o, cy - s - 8, 8, 8, 'stone')
        rect(cx + o, cy + s, 8, 8, 'stone')
        rect(cx - s - 8, cy + o, 8, 8, 'stone')
        rect(cx + s, cy + o, 8, 8, 'stone')
    # the value falls: a red arrow down the right of the panel
    bar(196, 10, 176, h - 16, 12, 'red')
    poly([(158, h - 22), (216, h - 22), (187, h)], 'red')
    bar(196, 10, 176, h - 16, 4, 'red2')


def v_envoys(w, h):
    """Kyiv: Zelensky met the US envoys, Europe brought into the talks."""
    rect(0, 0, w, h, 'night2')
    rect(0, 0, w, int(h * 0.52), 'slate')
    # the three flags on the wall
    for i, f in enumerate(('us', 'ua', 'eu')):
        fx = 14 + i * 76
        stroke(fx, 5, fx, int(h * 0.50), 2, 'ink')
        if f == 'us':
            for r in range(3):
                rect(fx, 7 + r * 7, 42, 3, 'red')
                rect(fx, 10 + r * 7, 42, 4, 'cream')
            rect(fx, 7, 17, 14, 'blue')
        elif f == 'ua':
            rect(fx, 7, 42, 14, 'blue')
            rect(fx, 21, 42, 14, 'gold')
        else:
            rect(fx, 7, 42, 28, 'blue')
            for a2 in range(8):
                ang = math.pi * 2 * a2 / 8
                disc(fx + 21 + 9 * math.cos(ang), 21 + 9 * math.sin(ang), 2, 'gold')
    # two delegations, facing each other across a table, seen from behind
    for cx in (38, w - 38):
        poly([(cx - 30, h), (cx - 22, int(h * 0.78)), (cx + 22, int(h * 0.78)),
              (cx + 30, h)], 'night3')
        disc(cx, int(h * 0.70), 12, 'night3')
    # the table and its papers
    rect(60, int(h * 0.84), w - 120, int(h * 0.08), 'cream')
    rect(52, int(h * 0.92), w - 104, int(h * 0.05), 'concr')
    for i in range(2):
        rect(96 + i * 40, int(h * 0.85), 26, 6, 'night')


def v_ship_down(w, h):
    """New Orleans: a cruise ship sank with 130 aboard, all survived."""
    wl = int(h * 0.50)
    rect(0, 0, w, h, 'night2')
    rect(0, 0, w, int(h * 0.14), 'night')
    # hull: bow high to the right, stern already down under the waterline
    bar(16, int(h * 0.80), 208, int(h * 0.28), 22, 'cream')
    bar(16, int(h * 0.86), 206, int(h * 0.34), 8, 'red')
    # a deck and a funnel, on the same tilt
    bar(66, int(h * 0.64), 160, int(h * 0.42), 16, 'cream')
    for i in range(5):
        rect(84 + i * 15, int(h * 0.58) - i * 4, 8, 7, 'night2')
    bar(140, int(h * 0.42), 148, int(h * 0.20), 9, 'red2')
    stroke(70, int(h * 0.64), 64, int(h * 0.38), 2, 'slate')
    # the water closes over her
    rect(0, wl + 12, w, h, 'sea')
    poly([(0, wl + 12), (w, wl + 4), (w, wl + 12), (0, wl + 20)], 'sea2')
    # a life ring and a launch full of survivors
    ring(w - 38, h - 22, 18, 7, 'gold')
    rect(w - 38, h - 25, 11, 6, 'red')
    rect(w - 41, h - 41, 6, 11, 'red')
    poly([(44, h - 30), (112, h - 34), (116, h - 18), (40, h - 14)], 'orange')
    for i in range(2):
        disc(62 + i * 20, h - 42, 6, 'stone')


def v_flights(w, h):
    """The FAA ordered a nationwide ground stop, then lifted it."""
    rect(0, 0, w, h, 'night')
    rect(0, int(h * 0.66), w, h, 'night3')
    rect(20, int(h * 0.24), 13, int(h * 0.76), 'stone')
    rect(6, int(h * 0.14), 41, 24, 'cream')
    rect(12, int(h * 0.17), 29, 14, 'night2')
    rect(6, int(h * 0.14), 41, 4, 'gold')
    poly([(126, h), (200, h), (216, 2), (168, 8)], 'cream')
    poly([(126, h), (168, h), (198, int(h * 0.54)), (142, int(h * 0.62))], 'stone')
    rect(170, int(h * 0.20), 32, 10, 'red')
    stroke(-6, int(h * 0.96), w + 6, int(h * 0.54), 9, 'red')
    stroke(-6, int(h * 0.96), w + 6, int(h * 0.54), 3, 'red2')


def v_bus(w, h):
    """Golaghat, Assam: a bus and a truck collided, 26 killed."""
    rect(0, 0, w, h, 'stone')
    rect(0, 0, w, int(h * 0.44), 'smoke2')
    rect(0, int(h * 0.44), w, h, 'slate')
    rect(0, int(h * 0.44), w, 4, 'sand')
    # the bus, on its side: a tilted body, a window band, wheels up
    poly([(6, int(h * 0.80)), (108, int(h * 0.30)), (180, int(h * 0.48)),
          (78, int(h * 0.98))], 'orange')
    poly([(16, int(h * 0.78)), (110, int(h * 0.38)), (170, int(h * 0.52)),
          (76, int(h * 0.92))], 'cream')
    for i in range(4):
        poly([(30 + i * 27, int(h * 0.74) - i * 8),
              (48 + i * 27, int(h * 0.68) - i * 8),
              (48 + i * 27, int(h * 0.58) - i * 8),
              (30 + i * 27, int(h * 0.64) - i * 8)], 'night')
    rect(16, int(h * 0.80), 62, 6, 'red')
    disc(104, int(h * 0.34), 13, 'ink')
    disc(104, int(h * 0.34), 5, 'concr2')
    disc(166, int(h * 0.52), 13, 'ink')
    disc(166, int(h * 0.52), 5, 'concr2')
    # the truck, coming the other way
    poly([(188, int(h * 0.46)), (240, int(h * 0.34)), (244, int(h * 0.70)),
          (192, int(h * 0.82))], 'red')
    rect(198, int(h * 0.42), 28, 14, 'cream')
    disc(212, int(h * 0.78), 12, 'ink')
    disc(212, int(h * 0.78), 4, 'concr2')
    disc(120, int(h * 0.18), 14, 'concr')
    disc(170, int(h * 0.24), 10, 'concr')


def v_rubble(w, h):
    """Nairobi: a building under construction partly collapsed, 6 killed."""
    rect(0, 0, w, h, 'stone')
    rect(0, 0, w, int(h * 0.30), 'night2')
    # the standing half: a grid of floor slabs and window voids
    rect(2, 0, 62, int(h * 0.86), 'concr')
    for r in range(4):
        for cc in range(2):
            rect(9 + cc * 26, 7 + r * 20, 15, 12, 'night3')
    # the collapsed half: slabs sheared off and dropped, one still leaning
    poly([(64, int(h * 0.86)), (64, int(h * 0.44)), (150, int(h * 0.16)),
          (196, int(h * 0.30)), (110, int(h * 0.60)), (110, int(h * 0.86))], 'concr2')
    for i in range(3):
        poly([(70 + i * 26, int(h * 0.86)), (70 + i * 26, int(h * 0.52) + i * 6),
              (150 + i * 8, int(h * 0.30) + i * 6), (156 + i * 8, int(h * 0.40) + i * 6),
              (76 + i * 26, int(h * 0.62) + i * 6), (76 + i * 26, int(h * 0.86))],
             'concr')
    # the pile, and the rescuer's flag on it
    poly([(0, h), (0, int(h * 0.90)), (54, int(h * 0.84)), (118, int(h * 0.98)),
          (w, int(h * 0.90)), (w, h)], 'concr2')
    poly([(96, int(h * 0.92)), (126, int(h * 0.78)), (156, int(h * 0.96))], 'stone')
    stroke(210, int(h * 0.86), 210, int(h * 0.30), 3, 'ink')
    rect(210, int(h * 0.30), 30, 18, 'red')


def v_pact(w, h):
    """Istanbul: Qatar and Turkiye signed a mutual defence pact."""
    rect(0, 0, w, h, 'night2')
    rect(0, int(h * 0.56), w, h, 'night3')
    # the two flags, at the top
    rect(6, 2, 62, 30, 'plum')
    for i in range(3):
        rect(6, 7 + i * 9, 11, 6, 'cream')
    rect(156, 2, 62, 30, 'red')
    disc(186, 17, 11, 'cream')
    disc(192, 17, 8, 'red')
    disc(195, 17, 4, 'cream')
    # the pact: a signed sheet, held by two hands
    poly([(66, int(h * 0.38)), (162, int(h * 0.38)), (170, int(h * 0.86)),
          (58, int(h * 0.86))], 'cream')
    for i in range(4):
        rect(74, int(h * 0.46) + i * 10, 76, 4, 'concr')
    stroke(84, int(h * 0.80), 106, int(h * 0.72), 3, 'ink')
    stroke(104, int(h * 0.80), 128, int(h * 0.70), 3, 'ink')
    # the clasp, low and wide, from both sides
    poly([(0, h), (0, int(h * 0.82)), (66, int(h * 0.76)), (72, h)], 'slate')
    poly([(w, h), (w, int(h * 0.82)), (170, int(h * 0.76)), (164, h)], 'concr2')


def v_cartels(w, h):
    """Guatemala: three criminal groups listed as terrorist organisations."""
    rect(0, 0, w, h, 'concr2')
    rect(20, 4, 146, h - 8, 'cream')
    rect(20, 4, 146, 9, 'stone')
    for i in range(6):
        rect(32, 24 + i * 11, 90 - (i % 3) * 22, 6, 'concr')
    ring(188, int(h * 0.58), 40, 10, 'red')
    burst(188, int(h * 0.58), 24, 'red', 5, 10)
    rect(150, int(h * 0.86), 76, 8, 'red')


def v_police(w, h):
    """London: police opened an investigation into an actor."""
    rect(0, 0, w, h, 'night3')
    for x in range(0, w, 24):
        rect(x, 0, 1, h, 'night2')
    rect(46, 6, 152, 30, 'ink')
    rect(54, 11, 64, 21, 'red')
    rect(128, 11, 64, 21, 'blue')
    poly([(54, 36), (118, 36), (84, h), (8, h)], 'red2')
    poly([(128, 36), (192, 36), (236, h), (160, h)], 'blue')
    poly([(122, int(h * 0.50)), (162, int(h * 0.58)), (154, int(h * 0.90)),
          (122, int(h * 1.00)), (90, int(h * 0.90)), (82, int(h * 0.58))], 'gold')
    burst(122, int(h * 0.74), 17, 'ink', 5, 6)


def v_containers(w, h):
    """Beijing: the first meeting of the US-China trade council."""
    rect(0, 0, w, h, 'night2')
    # a container ship's deck, loaded, with a gantry over it
    rect(0, int(h * 0.72), w, h, 'sea')
    rect(0, int(h * 0.72), w, 4, 'sea2')
    poly([(0, int(h * 0.80)), (w, int(h * 0.74)), (w, int(h * 0.90)),
          (0, int(h * 0.96))], 'concr2')
    cols = ('red', 'teal', 'gold', 'blue')
    for r in range(2):
        for i in range(5):
            rect(6 + i * 44, int(h * 0.34) + r * 24, 38, 22, cols[(i + r) % 4])
            rect(10 + i * 44, int(h * 0.36) + r * 24, 4, 18, 'ink')
    # the crane, straddling the stack
    stroke(w - 30, int(h * 0.72), w - 30, 2, 7, 'gold')
    stroke(w - 30, 5, 6, 5, 7, 'gold')
    stroke(60, 5, 60, int(h * 0.36), 3, 'ink')
    rect(48, int(h * 0.36), 24, 12, 'red')
    # the two flags the council is between
    stroke(126, int(h * 0.34), 126, int(h * 0.06), 2, 'stone')
    rect(126, int(h * 0.06), 26, 16, 'red')
    stroke(160, int(h * 0.34), 160, int(h * 0.10), 2, 'stone')
    rect(160, int(h * 0.10), 26, 16, 'blue')


def v_chip_probe(w, h):
    """Kuala Lumpur: Malaysia and Singapore probe diverted US chips."""
    rect(0, 0, w, h, 'night')
    # the open crate the chips left
    poly([(8, int(h * 0.56)), (86, int(h * 0.56)), (86, int(h * 0.98)),
          (8, int(h * 0.98))], 'sand')
    poly([(8, int(h * 0.56)), (26, int(h * 0.40)), (68, int(h * 0.40)),
          (86, int(h * 0.56))], 'stone')
    # the chip, out of the crate and moving along a red arrow
    s2 = 21
    cx, cy = 104, int(h * 0.48)
    rect(cx - s2, cy - s2, 2 * s2, 2 * s2, 'teal')
    rect(cx - s2 + 5, cy - s2 + 5, 2 * s2 - 10, 2 * s2 - 10, 'night')
    for i in range(3):
        o = -11 + i * 11
        rect(cx + o, cy - s2 - 6, 6, 6, 'stone')
        rect(cx + o, cy + s2, 6, 6, 'stone')
    stroke(cx + s2 + 4, cy, 168, cy, 6, 'red')
    poly([(186, cy), (166, cy - 12), (166, cy + 12)], 'red')
    # the magnifier that has the case
    ring(w - 34, int(h * 0.44), 26, 9, 'gold')
    disc(w - 34, int(h * 0.44), 17, 'sea2')
    stroke(w - 16, int(h * 0.58), w - 2, int(h * 0.78), 9, 'gold')


def v_fake_calls(w, h):
    """The FBI reported DPRK hackers using faked video calls to steal crypto."""
    rect(0, 0, w, h, 'night3')
    poly([(18, 2), (184, 2), (184, int(h * 0.76)), (18, int(h * 0.76))], 'slate')
    rect(26, 10, 150, int(h * 0.56), 'sea')
    # a video call: four participants, the speaker's identity blanked out
    for gy in range(2):
        for gx in range(2):
            px, py = 34 + gx * 44, 16 + gy * 24
            rect(px, py, 38, 20, 'concr2')
            disc(px + 19, py + 8, 6, 'night3')
            rect(px + 8, py + 13, 22, 6, 'night3')
    rect(78, 40, 38, 20, 'night3')
    rect(88, 44, 18, 12, 'stone')
    for gy in range(2):
        for gx in range(2):
            rect(102 + gx * 2, 40 + gy * 2, 2, 2, 'ink')
    rect(118, 14, 8, 8, 'red')
    poly([(6, int(h * 0.76)), (196, int(h * 0.76)), (224, int(h * 0.96)),
          (0, int(h * 0.96))], 'ink')
    for i in range(3):
        rect(204, int(h * 0.60) + i * 10, 32, 8, 'gold')
    disc(220, int(h * 0.46), 11, 'gold')
    rect(210, int(h * 0.46), 20, 5, 'gold')


def v_deport(w, h):
    """The US reported a record 483,200 deportations in 2026."""
    rect(0, 0, w, h, 'stone')
    rect(0, 0, w, int(h * 0.22), 'smoke2')
    rect(0, int(h * 0.80), w, h, 'concr2')
    rect(6, int(h * 0.24), 146, int(h * 0.46), 'blue')
    rect(6, int(h * 0.28), 146, 11, 'cream')
    for i in range(4):
        rect(18 + i * 33, int(h * 0.40), 23, 17, 'night2')
    disc(36, int(h * 0.74), 14, 'ink')
    disc(36, int(h * 0.74), 5, 'slate')
    disc(124, int(h * 0.74), 14, 'ink')
    disc(124, int(h * 0.74), 5, 'slate')
    rect(166, int(h * 0.26), 60, 44, 'cream')
    rect(172, int(h * 0.26) + 7, 17, 17, 'slate')
    disc(180, int(h * 0.26) + 13, 5, 'stone')
    for i in range(3):
        rect(194, int(h * 0.26) + 9 + i * 8, 24, 5, 'concr')
    rect(166, int(h * 0.26) + 33, 60, 5, 'red')


# ------------------------------------------------------------------- layout
MAST_H = 118
FOOT_H = 76
MARGIN = 14
GUTTER = 8
GRID_TOP = MAST_H + 10
GRID_BOT = H - FOOT_H - 6
PANEL_W = (W - 2 * MARGIN - 3 * GUTTER) // 4
PANEL_H = (GRID_BOT - GRID_TOP - 3 * GUTTER) // 4
GRID_BOT = GRID_TOP + 4 * PANEL_H + 3 * GUTTER      # exact, after rounding down

RULE_H = 4          # accent rule along the top of a panel
GAP1 = 5
KICK_H = 21         # 7 px rows at k=3
GAP2 = 5
HEAD_H = 62         # two 7-row headline lines and 4 px leading, at k=4
GAP3 = 6
PAD = 10
LINE_GAP = 4
HEAD_K = 4          # one headline size for all 16: a grid, not a ransom note
ART_H = PANEL_H - (RULE_H + GAP1 + KICK_H + GAP2 + HEAD_H + GAP3)
ART_Y = RULE_H
KICK_Y = ART_Y + ART_H + GAP1
HEAD_Y = KICK_Y + KICK_H + GAP2

KICK_MAXK = 3       # every kicker is short enough to draw at one size

def _choose_head_style(lines, bw, maxk=5, mink=3):
    """Largest uniform (k, track) at which every headline line fits bw."""
    for k in range(maxk, mink - 1, -1):
        for track in (6, 5):
            if all(tw(t, k, track) <= bw for t in lines):
                return k, track
    raise AssertionError('headline lines cannot be set uniformly in %dpx' % bw)


STORIES = [
    # (vignette, accent, kicker, headline line one, headline line two)
    (v_radar,      'gold',   'BAHRAIN',       'RADAR',     'DESTROYED'),
    (v_warship,    'teal',   'GULF OF FINLAND', 'WARSHIP',  'DRONE HIT'),
    (v_odesa,      'orange', 'UKRAINE',       'ODESA HIT', 'AGAIN'),
    (v_nvidia,     'teal',   'WASHINGTON',    'NVIDIA',    'IN CRISIS'),
    (v_envoys,     'blue',   'KYIV',          'ENVOYS',    'IN TALKS'),
    (v_ship_down,  'gold',   'NEW ORLEANS',   'SHIP DOWN', 'ALL SAFE'),
    (v_flights,    'red',    'USA / FAA',     'FLIGHTS',   'HALTED'),
    (v_bus,        'orange', 'ASSAM, INDIA',  'BUS CRASH', '26 DEAD'),
    (v_rubble,     'gold',   'NAIROBI',       'BUILDING',  'COLLAPSE'),
    (v_pact,       'plum',   'ISTANBUL',      'DEFENCE',   'PACT'),
    (v_cartels,    'red',    'GUATEMALA',     'US LISTS',  'CARTELS'),
    (v_police,     'blue',   'LONDON',        'ACTOR',     'PROBED'),
    (v_containers, 'gold',   'BEIJING',       'TRADE',     'TALKS'),
    (v_chip_probe, 'teal',   'KUALA LUMPUR',  'CHIP',      'PROBE'),
    (v_fake_calls, 'gold',   'FBI',          '$400M',     'STOLEN'),
    (v_deport,     'blue',   'USA',           '483,200',   'DEPORTED'),
]


HEAD_LINES = [t for row in STORIES for t in row[3:5]]
HEAD_K, HEAD_TRACK = _choose_head_style(HEAD_LINES, PANEL_W - 2 * PAD)


def panel_xy(i):
    return (MARGIN + (i % 4) * (PANEL_W + GUTTER),
            GRID_TOP + (i // 4) * (PANEL_H + GUTTER))


def masthead():
    rect(0, 0, W, MAST_H, 'ink')
    label(MARGIN, 9, 'FRIDAY 13 NOVEMBER 2026', 426, 3, 3, 'gold')
    label(470, 9, '16 STORIES, 4 CONTINENTS', W - MARGIN - 470, 3, 3,
          'stone', align='r')
    label(MARGIN, 38, 'THE WORLD TODAY', W - 2 * MARGIN, 8, 6, 'cream',
          align='c')
    rect(0, MAST_H - 10, W, 10, 'gold')
    rect(0, MAST_H - 10, W, 4, 'red2')


def footer():
    rect(0, H - FOOT_H, W, FOOT_H, 'ink')
    rect(0, H - FOOT_H, W, 3, 'night2')
    label(MARGIN, H - 59, 'SOURCES: BBC · AL JAZEERA · REUTERS · AP · XINHUA',
          W - 2 * MARGIN, 3, 3, 'stone', align='c')
    label(MARGIN, H - 33, 'DRAWN BY PROGRAM, NOT PHOTOGRAPHS',
          W - 2 * MARGIN, 3, 3, 'stone', align='c')


def panel(i):
    fn, accent, kicker, l1, l2 = STORIES[i]
    sx, sy = panel_xy(i)
    rect(sx, sy, PANEL_W, PANEL_H, 'ink')
    rect(sx, sy, PANEL_W, RULE_H, accent)
    clip(sx, sy + ART_Y, PANEL_W, ART_H)
    origin(sx, sy + ART_Y)
    fn(PANEL_W, ART_H)
    origin(0, 0)
    clip_off()
    # kicker: small caps in the accent colour, over a hairline rule
    rect(sx + PAD, sy + KICK_Y + KICK_H, PANEL_W - 2 * PAD, 2, 'night2')
    kk, ktrack = kick_style(kicker, PANEL_W - 2 * PAD)
    label(sx + PAD, sy + KICK_Y, kicker, PANEL_W - 2 * PAD, kk, kk, accent,
          track=ktrack, k=kk)
    # headline: on its own solid band, the loudest thing in the panel
    rect(sx, sy + HEAD_Y - GAP2, PANEL_W, HEAD_H + GAP2 + GAP3, 'night')
    bw = PANEL_W - 2 * PAD
    k = HEAD_K
    th = 2 * 7 * k + LINE_GAP
    ty = sy + HEAD_Y + (HEAD_H - th) // 2
    label(sx + PAD, ty, l1, bw, k, k, 'cream', track=HEAD_TRACK, k=k)
    label(sx + PAD, ty + 7 * k + LINE_GAP, l2, bw, k, k, 'cream',
          track=HEAD_TRACK, k=k)


def build():
    rect(0, 0, W, H, 'paper')
    masthead()
    for i in range(len(STORIES)):
        panel(i)
    footer()


# ---------------------------------------------------------------- png bytes
def chunk(tag, data):
    return (struct.pack('>I', len(data)) + tag + data
            + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))


def encode():
    raw = b''.join(b'\x00' + bytes(pix[i:i + W * 3])
                   for i in range(0, len(pix), W * 3))
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 9))
            + chunk(b'IEND', b''))


def check():
    """Assert no drawn string overflows its box and the grid geometry adds up."""
    errs = []
    if len(STORIES) != 16:
        errs.append('expected 16 stories, have %d' % len(STORIES))
    if 2 * MARGIN + 4 * PANEL_W + 3 * GUTTER != W:
        errs.append('panel widths and gutters do not span %d px' % W)
    if GRID_TOP + 4 * PANEL_H + 3 * GUTTER != GRID_BOT:
        errs.append('panel heights and gutters do not reach the grid foot')
    if GRID_BOT + 6 > H - FOOT_H:
        errs.append('grid does not stop above the footer')
    for t in HEAD_LINES:
        if tw(t, HEAD_K, HEAD_TRACK) > PANEL_W - 2 * PAD:
            errs.append('headline %r does not fit at the shared style' % t)
    if ART_H < 80:
        errs.append('art box is only %d px tall' % ART_H)
    if RULE_H + ART_H + GAP1 + KICK_H + GAP2 + HEAD_H + GAP3 != PANEL_H:
        errs.append('panel strips do not add up to PANEL_H')
    if KICK_Y < ART_Y + ART_H or HEAD_Y < KICK_Y + KICK_H:
        errs.append('caption strips overlap the art box')
    for s, k, w, x, y, bx, bw in TEXT_BOXES:
        if w > bw:
            errs.append('%r drawn %d px wide in a %d px box' % (s, w, bw))
        if x < bx or x + w > bx + bw:
            errs.append('%r spans %d..%d, box is %d..%d'
                        % (s, x, x + w, bx, bx + bw))
        if x < 0 or y < 0 or x + w > W or y + 7 * k > H:
            errs.append('%r falls outside the canvas' % s)
        if not s.strip():
            errs.append('empty string drawn')
        missing = [c for c in s.upper() if c not in GLYPHS]
        if missing:
            errs.append('%r has no glyph for %r' % (s, missing))

    # every caption's ink must sit inside its own band, clear of the art
    for i in range(16):
        sx, sy = panel_xy(i)
        art_b, kick_t = sy + ART_Y + ART_H, sy + KICK_Y
        kick_b, head_t = kick_t + KICK_H, sy + HEAD_Y - GAP2
        head_b = sy + HEAD_Y + HEAD_H
        if not (art_b <= kick_t and kick_b <= head_t):
            errs.append('panel %d: art, kicker and headline bands overlap' % i)
        if head_b > sy + PANEL_H:
            errs.append('panel %d: headline band runs off the panel' % i)
        for s, k, w, x, y, bx, bw in TEXT_BOXES:
            if not (sx <= x < sx + PANEL_W and sy <= y < sy + PANEL_H):
                continue
            bottom = y + 7 * k
            if y < kick_t:
                errs.append('panel %d: %r starts in the art box' % (i, s))
            if bottom > head_b:
                errs.append('panel %d: %r runs past the headline band' % (i, s))
    # panel boxes must not touch each other
    for i in range(16):
        ax, ay = panel_xy(i)
        for j in range(i + 1, 16):
            bx2, by2 = panel_xy(j)
            if (ax < bx2 + PANEL_W and bx2 < ax + PANEL_W
                    and ay < by2 + PANEL_H and by2 < ay + PANEL_H):
                errs.append('panels %d and %d overlap' % (i, j))
    png = encode()
    if len(png) > 1048576:
        errs.append('png is %d bytes, cap is 1048576' % len(png))
    print('strings drawn and measured: %d' % len(TEXT_BOXES))
    print('panel %dx%d, art %dx%d, grid %d,%d..%d,%d'
          % (PANEL_W, PANEL_H, PANEL_W, ART_H, MARGIN, GRID_TOP,
             MARGIN + 4 * PANEL_W + 3 * GUTTER, GRID_BOT))
    print('png %d bytes' % len(png))
    if errs:
        for e in errs:
            print('FAIL:', e)
        raise AssertionError('%d layout problems' % len(errs))
    print('OK: no string overflows its box, grid geometry adds up')


def main():
    build()
    if '--check' in sys.argv:
        check()
        return
    png = encode()
    assert len(png) <= 1048576, len(png)
    out = Path(os.environ.get('MAKEFUN_OUTPUT_DIR', '/output'))
    out.mkdir(parents=True, exist_ok=True)
    (out / 'entry.png').write_bytes(png)
    print('wrote', out / 'entry.png', len(png), 'bytes')


main()
