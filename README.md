# The World Today - 13 November 2026

One 1024 x 1024 editorial front page, drawn from primitives, for make.fun's
`news-image-01` challenge: sum up Friday 13 November 2026 in a single image.

Sixteen stories, sixteen equal panels, four continents. The program is Python
3, standard library only. No network, no external assets, no fonts, no clock,
no randomness: two runs write byte-identical files.

This is an illustration drawn by code from written reports. It is not a
photograph, and the footer of the page says so.

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py     # writes out/entry.png
python3 main.py --check                    # measures the page, writes nothing
```

With `MAKEFUN_OUTPUT_DIR` unset it writes `/output/entry.png`. Output is a
single 1024 x 1024 PNG, about 28 KiB, well under the 1 MiB cap, and a run takes
about 0.3 s on one CPU.

## What the picture shows

A masthead - "THE WORLD TODAY", "FRIDAY 13 NOVEMBER 2026", "16 STORIES, 4
CONTINENTS" - and then a 4 x 4 grid of equal panels. Each panel is, top to
bottom: an accent rule, a flat vignette, a place kicker, and a two-line
headline in white caps on a solid dark band. A thin footer carries the source
list and the line "DRAWN BY PROGRAM, NOT PHOTOGRAPHS".

Equal panels are deliberate. Breadth is the point: a reader who missed the day
should see at a glance that it was not one story in one country.

### The 16 panels, in order

Every story below was reported on 13 November 2026 and was checked against that
day's current-events record and the outlets named in the footer before it went
in. No detail, number or attribution is invented.

| # | Place | Headline | What the panel draws |
|---|-------|----------|----------------------|
| 1 | Bahrain | RADAR DESTROYED | A radar dome on a platform, hit, with a missile trail in |
| 2 | Gulf of Finland | WARSHIP / DRONE HIT | A heeling warship with a hit flash and a drone overhead |
| 3 | Odesa, Ukraine | ODESA HIT / AGAIN | A dark skyline lit by windows, under two drone trails |
| 4 | Washington | NVIDIA / IN CRISIS | A cracked microchip and a falling red arrow |
| 5 | Kyiv | ENVOYS / IN TALKS | Three flags (US, Ukraine, EU) over two delegations at a table |
| 6 | New Orleans | SHIP DOWN / ALL SAFE | A listed cruise hull cut by the waterline, a life ring |
| 7 | USA / FAA | FLIGHTS / HALTED | An airliner fin beside a control tower, crossed by a stop bar |
| 8 | Golaghat, Assam | BUS CRASH / 26 DEAD | A bus on its side and a truck's nose, in dust |
| 9 | Nairobi | BUILDING / COLLAPSE | A standing wall of floor slabs beside a sheared, fallen half |
| 10 | Istanbul | DEFENCE / PACT | The Qatari and Turkish flags over a signed sheet and a clasp |
| 11 | Guatemala | US LISTS / CARTELS | A listed document with a red stamp over it |
| 12 | London | ACTOR / PROBED | A police light bar, its beams, and a badge |
| 13 | Beijing | TRADE / TALKS | A loaded container ship under a gantry, US and Chinese flags |
| 14 | Kuala Lumpur | CHIP / PROBE | An open crate, a chip on a red arrow, a magnifier |
| 15 | FBI | $400M / STOLEN | A laptop on a call, its speaker's face blanked out, coins |
| 16 | USA | 483,200 / DEPORTED | A coach, an ID card, and a rising bar |

The facts each panel stands for, in one line each:

1. Iran said it destroyed a US early-warning radar in Bahrain, retaliation for a
   US strike on telecoms infrastructure at Sirik.
2. A Ukrainian drone struck a Russian warship in the Gulf of Finland.
3. Russian drone strikes hit Odesa and Sumy.
4. Nvidia's Jensen Huang stepped down amid a spy scandal; the Senate Banking
   Committee summoned him and Commerce Secretary Lutnick to testify.
5. President Zelensky met the US envoys Witkoff and Kushner, with Europe brought
   into the talks.
6. A tanker collided with the cruise ship American Heritage on the Mississippi;
   she sank with 130 aboard, and all aboard survived.
7. The FAA ordered a nationwide ground stop over a communications failure; it
   was later lifted.
8. A bus and a truck collided at Golaghat, Assam: 26 killed, 11 injured.
9. An under-construction building partially collapsed in Nairobi: 6 killed,
   5 injured.
10. Qatar and Turkiye signed a mutual defence pact in Istanbul.
11. The US State Department designated three Guatemalan criminal groups as
    foreign terrorist organisations.
12. The Metropolitan Police opened a criminal investigation into the actor
    David Walliams over alleged serious sexual offences.
13. China and the US held the first meeting of their trade council, discussing
    tariff cuts and agricultural trade.
14. Malaysia and Singapore are investigating whether the firm Megaspeed diverted
    US chips to China.
15. North Korean hackers used faked video calls to steal about USD 400m in
    cryptocurrency.
16. The US reported a record 483,200 deportations in 2026.

Two headlines are shorter than the underlying report on purpose, because the
panel is 243 px wide and the reader sees it at about 70 px. "SHIP DOWN / ALL
SAFE" is the collision, the sinking and the survival; "FLIGHTS / HALTED" is the
ground stop, later lifted. Nothing is added that the reports did not say.

## Layout rules

Every string is measured before it is drawn.

- `tw()` returns the exact pixel width of a string at a glyph scale.
- `fit()` returns the largest scale in a given range whose rendering fits a box.
- `label()` fits a string to a box, draws it, and records the exact box it
  occupies in `TEXT_BOXES`.
- `--check` walks every recorded string and fails if any is wider than its box,
  starts left of it, leaves the canvas, contains a character with no glyph, or
  lands in the art box rather than its own caption band.

The page grids are derived, not typed in: panel width comes from the canvas
width and the gutters, panel height from the grid height, and the art box from
what the caption strips leave. `--check` re-derives them and asserts that the
widths and gutters span exactly 1024 px, that the heights and gutters reach the
grid foot, that the panel strips add up to the panel height, that the art,
kicker and headline bands do not overlap, that no two panels overlap, and that
the PNG is within the size cap.

Caption scales are fixed for the page as a whole rather than chosen per panel:
all 16 kickers set at one scale and tracking, all 32 headline lines at one
scale and tracking (`_choose_head_style` picks the largest pair at which every
line fits). A grid set in a dozen different sizes looks like a ransom note; one
size looks like a newspaper.

## Determinism

No randomness, no clock, no environment-dependent input except
`MAKEFUN_OUTPUT_DIR`, and no iteration over unordered containers. Two runs
produce byte-identical files:

```
$ MAKEFUN_OUTPUT_DIR=/tmp/a python3 main.py && MAKEFUN_OUTPUT_DIR=/tmp/b python3 main.py
$ sha256sum /tmp/a/entry.png /tmp/b/entry.png
3a1934717a0a7e7872db2475c4a1561e7ebf817e64447d226890bb45b7615290  /tmp/a/entry.png
3a1934717a0a7e7872db2475c4a1561e7ebf817e64447d226890bb45b7615290  /tmp/b/entry.png
```

The PNG is written in one pass: a single `IDAT` chunk of filter-0 scanlines,
with correct CRCs on every chunk, and no ancillary chunks.

## Files

- `main.py` - the program.
- `entry.png` - the rendered image at the last commit that updated it.
- `LICENSE` - MIT.
