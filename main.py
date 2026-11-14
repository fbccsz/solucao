"""The World Today - an editorial front page for Friday 13 November 2026.

Sixteen stories on one page, a 4x4 grid of equal panels under a masthead.
Standard library only, no network, no external assets, no randomness, no
clock: two runs write byte-identical files.  Writes one 1024x1024 PNG to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).

    python3 main.py            write the PNG
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
# Placeholders for now: one flat field per story.  The real vignettes replace
# these in the next commit; this one is about the page, the grid and the type.

def v_radar(w, h):
    rect(0, 0, w, h, 'night2')
    rect(0, int(h * 0.5), w, int(h * 0.5), 'night3')


def v_warship(w, h):
    rect(0, 0, w, h, 'night2')
    rect(0, int(h * 0.5), w, int(h * 0.5), 'night3')


def v_odesa(w, h):
    rect(0, 0, w, h, 'night2')
    rect(0, int(h * 0.5), w, int(h * 0.5), 'night3')


def v_nvidia(w, h):
    rect(0, 0, w, h, 'night2')
    rect(0, int(h * 0.5), w, int(h * 0.5), 'night3')


def v_envoys(w, h):
    rect(0, 0, w, h, 'night2')
    rect(0, int(h * 0.5), w, int(h * 0.5), 'night3')


def v_ship_down(w, h):
    rect(0, 0, w, h, 'night2')
    rect(0, int(h * 0.5), w, int(h * 0.5), 'night3')


def v_flights(w, h):
    rect(0, 0, w, h, 'night2')
    rect(0, int(h * 0.5), w, int(h * 0.5), 'night3')


def v_bus(w, h):
    rect(0, 0, w, h, 'night2')
    rect(0, int(h * 0.5), w, int(h * 0.5), 'night3')


def v_rubble(w, h):
    rect(0, 0, w, h, 'night2')
    rect(0, int(h * 0.5), w, int(h * 0.5), 'night3')


def v_pact(w, h):
    rect(0, 0, w, h, 'night2')
    rect(0, int(h * 0.5), w, int(h * 0.5), 'night3')


def v_cartels(w, h):
    rect(0, 0, w, h, 'night2')
    rect(0, int(h * 0.5), w, int(h * 0.5), 'night3')


def v_police(w, h):
    rect(0, 0, w, h, 'night2')
    rect(0, int(h * 0.5), w, int(h * 0.5), 'night3')


def v_containers(w, h):
    rect(0, 0, w, h, 'night2')
    rect(0, int(h * 0.5), w, int(h * 0.5), 'night3')


def v_chip_probe(w, h):
    rect(0, 0, w, h, 'night2')
    rect(0, int(h * 0.5), w, int(h * 0.5), 'night3')


def v_fake_calls(w, h):
    rect(0, 0, w, h, 'night2')
    rect(0, int(h * 0.5), w, int(h * 0.5), 'night3')


def v_deport(w, h):
    rect(0, 0, w, h, 'night2')
    rect(0, int(h * 0.5), w, int(h * 0.5), 'night3')


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


def main():
    build()
    png = encode()
    assert len(png) <= 1048576, len(png)
    out = Path(os.environ.get('MAKEFUN_OUTPUT_DIR', '/output'))
    out.mkdir(parents=True, exist_ok=True)
    (out / 'entry.png').write_bytes(png)
    print('wrote', out / 'entry.png', len(png), 'bytes')


main()
